# overdue – know who owes you, and what to send today

A tiny offline Python tool for freelancers: feed it an invoice CSV, get a list of late invoices with days late, open amounts and the right reminder stage, plus ready-to-edit draft emails.

## What it does

- Reads a CSV of invoices (open/paid, partial payments supported).
- Calculates due date, days late and open amount, sorted by most overdue.
- Suggests a stage: `heads-up` (3 days before due), `nudge` (1+ days), `first` (7+), `second` (14+), `final` (30+).
- Creates plain-text draft emails (English) for each stage.
- Safe by design: no network, no deletions, **dry-run by default**. With `--write` it only creates new files in the drafts folder and never overwrites existing ones.

## Quick start

```bash
python overdue.py invoices.example.csv --today 2026-10-15
# looks fine? create the drafts:
python overdue.py invoices.example.csv --today 2026-10-15 --write --out drafts
```

CSV header: `number,client,invoice_date,terms_days,amount,paid_so_far,status` (dates `YYYY-MM-DD`, status `open` or `paid`). Use `--currency USD` to change the currency label.

## Requirements

Python 3.8+ (standard library only).

The drafts are communication aids, not legal advice. Check local rules before mentioning late fees or consequences.

Created with AI assistance by an automated system.

## Full version

The lite version is a command-line tool with five English email stages. The paid Payment Reminder Kit for Freelancers adds:

- 12 reviewed reminder emails in English and German (Word and plain text), including partial-payment, resend-invoice, agency and thank-you messages
- An Excel overdue tracker with days-late formulas, a "next step" column, settings and a weekly overview
- A one-page escalation timeline and quick-start guide (PDF)

Get it here: https://kontor7-agent.github.io/p/payment-reminder-kit-for-freelancers?s=github

## License

MIT, see `LICENSE`.
