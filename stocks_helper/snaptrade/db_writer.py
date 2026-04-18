import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stocks_web.settings")
django.setup()

from dashboard.models import Journal
from .transaction_parser import parse_transactions_db, populate_transactions_db


def write_journal_to_db():
    """
    Parse *unprocessed* SnapTrade transactions and append their corresponding
    double-entry accounting rows to the database ledger.

    This function assumes `parse_transactions_db()` already performs
    transaction-level deduplication via processed transaction IDs.

    `parse_transactions_db()` is a generator that yields:

        Generator[tuple[str, list[list[str]]]]

    Meaning:
        For each transaction, it yields:
            (tx_id, rows)

        where:
            tx_id: str
            rows: list of 5-element lists:
                  [Date, Account, Debit, Credit, Description]

    Behavior:
    - Iterates transaction-by-transaction.
    - Skips empty row sets.
    - Inserts each valid journal row into the database.

    Returns:
        list[tuple[str, list[list[str]]]]:
            List of successfully written (tx_id, rows) pairs.
    """

    written = []

    for tx_id, rows in parse_transactions_db():
        if not rows:
            continue

        for row in rows:
            if not isinstance(row, (list, tuple)) or len(row) != 5:
                continue

            Journal.objects.create(
                date=row[0],
                account=row[1],
                debit=row[2],
                credit=row[3],
                description=row[4],
                tx_id_id=tx_id,
            )

        written.append((tx_id, rows))

    return written







def write_transactions_to_db(force: bool = False):
    """
    This function wrrites transactions to the database. 
    Behavior: 
    - recieves a dict of transaction field values from transaction_parser.py
    - initilizes django using django.setup() 
    - creates a Transaction object for each transaction and saves it to the database using the Django ORM.  
    """ 
    
    from dashboard.models import Transaction
    from .transaction_parser import populate_transactions_db
    count_created = 0
    count_updated = 0
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stocks_web.settings")
    django.setup()

    for tx in populate_transactions_db(force=force):
        # If transaction_id can be None, skip — PK can't be null
        if not tx.get("transaction_id"):
            continue

        obj, created = Transaction.objects.update_or_create(
            transaction_id=tx["transaction_id"],
            defaults={
                "stock_symbol": tx.get("stock_symbol", ""),
                "tx_type": tx.get("tx_type", ""),
                "description": tx.get("description", ""),
                "currency": tx.get("currency", ""),
                "amount": tx.get("amount"),
                "price": tx.get("price"),
                "units": tx.get("units"),
                "fee": tx.get("fee"),
                "fx_rate": tx.get("fx_rate"),
                "date": tx.get("date"),
            },
        )
        if created:
            count_created += 1
        else:
            count_updated += 1

    print(f"Transactions written: created={count_created}, updated={count_updated}")