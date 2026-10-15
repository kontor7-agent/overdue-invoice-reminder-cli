#!/usr/bin/env python3
"""overdue - read an invoice CSV, show who is late and which reminder to send.

Offline only. Reads one CSV file. Writes nothing unless --write is given;
with --write it only creates new .txt draft files inside --out (never
overwrites or deletes).

CSV columns (header required):
  number,client,invoice_date,terms_days,amount,paid_so_far,status
  invoice_date = YYYY-MM-DD, status = open or paid (paid_so_far optional)
"""
import argparse
import csv
import re
import sys
from datetime import date, datetime, timedelta

# (min days late, stage name)
STAGES = [
    (30, "final"),
    (14, "second"),
    (7, "first"),
    (1, "nudge"),
    (-3, "heads-up"),
]

TEMPLATES = {
    "heads-up": (
        "Upcoming due date: invoice {number}",
        "Hi {client},\n\nA quick heads-up: invoice {number} ({amount} {cur}) is due on {due}.\n"
        "Please let me know if you need anything from my side to process it.\n\nBest regards,\n[Your name]\n",
    ),
    "nudge": (
        "Invoice {number}: friendly reminder",
        "Hi {client},\n\nInvoice {number} ({open_amt} {cur} open) was due on {due}. It may have crossed "
        "your desk, so I wanted to check in. Could you confirm when I can expect payment?\n\n"
        "Thank you and best regards,\n[Your name]\n",
    ),
    "first": (
        "Invoice {number}: {days} days overdue",
        "Hi {client},\n\nI have not yet received payment for invoice {number} ({open_amt} {cur}), "
        "due on {due} ({days} days ago). Please send it this week or tell me the expected payment date.\n\n"
        "Best regards,\n[Your name]\n",
    ),
    "second": (
        "Invoice {number}: second reminder",
        "Hello {client},\n\nInvoice {number} ({open_amt} {cur}) is now {days} days past its due date of {due}. "
        "Please arrange payment within 7 days, or contact me if something is blocking it.\n\n"
        "Regards,\n[Your name]\n",
    ),
    "final": (
        "Invoice {number}: final notice",
        "Hello {client},\n\nDespite earlier messages, invoice {number} ({open_amt} {cur}) remains unpaid "
        "{days} days after {due}. Please pay within 7 days or call me to agree on a solution. "
        "[Optional: add consequences only after checking with a qualified person.]\n\nRegards,\n[Your name]\n",
    ),
}


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("csv_file")
    p.add_argument("--today", help="override today's date (YYYY-MM-DD)")
    p.add_argument("--currency", default="EUR")
    p.add_argument("--write", action="store_true", help="actually write draft files (default: dry-run)")
    p.add_argument("--out", default="drafts", help="folder for drafts (default: ./drafts)")
    return p.parse_args()


def stage_for(days_late):
    for limit, name in STAGES:
        if days_late >= limit:
            return name
    return None


def num(s):
    s = (s or "").strip().replace(",", ".")
    return float(s) if s else 0.0


def safe(s):
    return re.sub(r"[^A-Za-z0-9_-]+", "_", s).strip("_") or "x"


def main():
    a = parse_args()
    try:
        today = datetime.strptime(a.today, "%Y-%m-%d").date() if a.today else date.today()
    except ValueError:
        sys.exit("--today must be YYYY-MM-DD")
    rows = []
    try:
        with open(a.csv_file, newline="", encoding="utf-8-sig") as f:
            for i, r in enumerate(csv.DictReader(f), start=2):
                if (r.get("status") or "open").strip().lower() == "paid":
                    continue
                try:
                    inv = datetime.strptime(r["invoice_date"].strip(), "%Y-%m-%d").date()
                    terms = int(r["terms_days"])
                    amount = num(r["amount"])
                    paid = num(r.get("paid_so_far"))
                except (KeyError, ValueError, AttributeError):
                    print(f"line {i}: skipped (check columns/date/number format)", file=sys.stderr)
                    continue
                due = inv + timedelta(days=terms)
                rows.append((r["number"].strip(), r["client"].strip(), due, (today - due).days, amount - paid))
    except OSError as e:
        sys.exit(f"cannot read file: {e}")

    rows.sort(key=lambda x: -x[3])
    print(f"Today: {today}   Open invoices: {len(rows)}\n")
    print(f"{'Invoice':<12}{'Client':<22}{'Due':<12}{'Days late':>9}{'Open':>12}  Next step")
    total = 0.0
    drafts = []
    for number, client, due, late, open_amt in rows:
        st = stage_for(late)
        total += open_amt if late > 0 else 0
        print(f"{number:<12}{client[:21]:<22}{due!s:<12}{late:>9}{open_amt:>12.2f}  {st or 'wait'}")
        if st:
            subj, body = TEMPLATES[st]
            d = dict(number=number, client=client, due=due, days=late, amount=f"{open_amt:.2f}",
                     open_amt=f"{open_amt:.2f}", cur=a.currency)
            drafts.append((f"{safe(number)}_{st}.txt", "Subject: " + subj.format(**d) + "\n\n" + body.format(**d)))
    print(f"\nTotal overdue: {total:.2f} {a.currency}")

    if not drafts:
        return
    if not a.write:
        print(f"\nDry run: {len(drafts)} draft(s) would be written to '{a.out}'. Add --write to create them.")
        return
    import os
    os.makedirs(a.out, exist_ok=True)
    for name, text in drafts:
        path = os.path.join(a.out, name)
        if os.path.exists(path):
            print(f"exists, skipped: {path}")
            continue
        with open(path, "x", encoding="utf-8") as f:
            f.write(text)
        print(f"written: {path}")


if __name__ == "__main__":
    main()
