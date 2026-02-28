from decimal import Decimal

from bookkeeping import BookkeepingSystem


def test_add_accounts_and_record_entry() -> None:
    system = BookkeepingSystem()
    system.add_account("Cash")
    system.add_account("Revenue")

    system.record_entry(
        debit_account="Cash",
        credit_account="Revenue",
        amount=Decimal("125.50"),
        description="Consulting invoice",
        entry_date="2026-01-02",
    )

    trial_balance = system.trial_balance()
    assert trial_balance["Cash"] == "125.50"
    assert trial_balance["Revenue"] == "-125.50"


def test_ledger_for_account_filters_entries() -> None:
    system = BookkeepingSystem()
    for account in ("Cash", "Revenue", "Rent Expense"):
        system.add_account(account)

    system.record_entry("Cash", "Revenue", Decimal("100"), "Sale")
    system.record_entry("Rent Expense", "Cash", Decimal("30"), "Rent paid")

    cash_entries = system.ledger_for_account("Cash")
    assert len(cash_entries) == 2
    assert {entry.description for entry in cash_entries} == {"Sale", "Rent paid"}
