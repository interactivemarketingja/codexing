from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Dict, List


@dataclass
class Entry:
    date: str
    description: str
    debit_account: str
    credit_account: str
    amount: str


class BookkeepingSystem:
    """A lightweight double-entry bookkeeping system backed by JSON."""

    def __init__(self) -> None:
        self.accounts: Dict[str, Decimal] = {}
        self.entries: List[Entry] = []

    def add_account(self, name: str) -> None:
        if name in self.accounts:
            raise ValueError(f"Account '{name}' already exists")
        self.accounts[name] = Decimal("0")

    def record_entry(
        self,
        debit_account: str,
        credit_account: str,
        amount: Decimal,
        description: str,
        entry_date: str | None = None,
    ) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if debit_account not in self.accounts:
            raise ValueError(f"Unknown debit account: {debit_account}")
        if credit_account not in self.accounts:
            raise ValueError(f"Unknown credit account: {credit_account}")

        posted_date = entry_date or date.today().isoformat()
        self.accounts[debit_account] += amount
        self.accounts[credit_account] -= amount
        self.entries.append(
            Entry(
                date=posted_date,
                description=description,
                debit_account=debit_account,
                credit_account=credit_account,
                amount=str(amount),
            )
        )

    def trial_balance(self) -> Dict[str, str]:
        return {
            account: f"{balance:.2f}"
            for account, balance in sorted(self.accounts.items(), key=lambda item: item[0])
        }

    def ledger_for_account(self, account: str) -> List[Entry]:
        if account not in self.accounts:
            raise ValueError(f"Unknown account: {account}")
        return [
            entry
            for entry in self.entries
            if entry.debit_account == account or entry.credit_account == account
        ]

    def save(self, file_path: str | Path) -> None:
        path = Path(file_path)
        payload = {
            "accounts": {name: str(balance) for name, balance in self.accounts.items()},
            "entries": [asdict(entry) for entry in self.entries],
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, file_path: str | Path) -> "BookkeepingSystem":
        path = Path(file_path)
        system = cls()
        if not path.exists():
            return system

        payload = json.loads(path.read_text(encoding="utf-8"))
        system.accounts = {
            name: Decimal(balance) for name, balance in payload.get("accounts", {}).items()
        }
        system.entries = [Entry(**entry) for entry in payload.get("entries", [])]
        return system


def _decimal(value: str) -> Decimal:
    try:
        amount = Decimal(value)
    except InvalidOperation as exc:
        raise argparse.ArgumentTypeError(f"Invalid decimal amount: {value}") from exc
    if amount <= 0:
        raise argparse.ArgumentTypeError("Amount must be positive")
    return amount


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Simple bookkeeping CLI")
    parser.add_argument("--file", default="bookkeeping.json", help="JSON data file")

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_account = subparsers.add_parser("add-account", help="Create a new account")
    add_account.add_argument("name")

    record = subparsers.add_parser("record", help="Record a double-entry transaction")
    record.add_argument("debit_account")
    record.add_argument("credit_account")
    record.add_argument("amount", type=_decimal)
    record.add_argument("description")
    record.add_argument("--date", dest="entry_date")

    trial_balance = subparsers.add_parser("trial-balance", help="Show trial balance")
    trial_balance.set_defaults(command="trial-balance")

    ledger = subparsers.add_parser("ledger", help="Show account ledger")
    ledger.add_argument("account")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    system = BookkeepingSystem.load(args.file)

    if args.command == "add-account":
        system.add_account(args.name)
        system.save(args.file)
        print(f"Added account: {args.name}")
    elif args.command == "record":
        system.record_entry(
            debit_account=args.debit_account,
            credit_account=args.credit_account,
            amount=args.amount,
            description=args.description,
            entry_date=args.entry_date,
        )
        system.save(args.file)
        print("Entry recorded")
    elif args.command == "trial-balance":
        for account, balance in system.trial_balance().items():
            print(f"{account}: {balance}")
    elif args.command == "ledger":
        for entry in system.ledger_for_account(args.account):
            print(
                f"{entry.date} | {entry.description} | "
                f"DR {entry.debit_account} / CR {entry.credit_account} | {entry.amount}"
            )


if __name__ == "__main__":
    main()
