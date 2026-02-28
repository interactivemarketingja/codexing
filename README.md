# Bookkeeping System

A lightweight **double-entry bookkeeping system** implemented in Python.

## Features
- Create accounts
- Record balanced journal entries (debit/credit)
- Print a trial balance
- Show ledger entries for a specific account
- Persist data in a JSON file

## Quick start

```bash
python bookkeeping.py --file books.json add-account Cash
python bookkeeping.py --file books.json add-account Revenue
python bookkeeping.py --file books.json record Cash Revenue 250.00 "Website project"
python bookkeeping.py --file books.json trial-balance
python bookkeeping.py --file books.json ledger Cash
```

## Run tests

```bash
python -m pytest -q
```
