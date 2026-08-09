import json

import json
import os

def find_credited_invst_amount(sold_shares, ticker, file_path=None, db=False, is_option=False):
    """
    Calculates the total credited amount when selling a number of shares for a given stock ticker.
    
    It reads from a JSON file that tracks share lots (price + date) and updates it to reflect
    the sold shares. The lots are consumed in FIFO order as per their appearance in the file.

    Args:
        sold_shares (float): The number of shares being sold.
        ticker (str): The stock symbol.
        file_path (str, optional): Path to the stocks JSON file. If not provided, defaults to 'stocks.json'
                                   in the same directory as this script.

    Returns:
        float: Total amount credited based on shares sold and their original purchase prices.

    Raises:
        FileNotFoundError: If the specified JSON file doesn't exist.
        ValueError: If not enough shares are available to fulfill the sell request.
    """
    base_path = os.path.dirname(__file__)
    if file_path is None:
        file_path = os.path.join(base_path, "stocks.json")
    if db:
        file_path = os.path.join(base_path, "stocks_db.json")  

        
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} does not exist.")

    with open(file_path, "r") as f:
        stocks = json.load(f)

    total_amount = 0
    requested_shares = sold_shares
    for price_date, available_shares in stocks.get(ticker, {}).items():
        if is_option and not price_date.endswith("_option"):
            continue
        if not is_option and price_date.endswith("_option"):
            continue
        if sold_shares > available_shares:
            total_amount += float(price_date.split('_')[0]) * available_shares
            sold_shares -= available_shares  
            stocks[ticker][price_date] = 0  
        else:
            total_amount += sold_shares * float(price_date.split('_')[0])
            stocks[ticker][price_date] -= sold_shares
            sold_shares = 0
            break
    if sold_shares > 0:
        # Either ticker not found or not enough shares, write to file named wrong_stocks.json for debugging
        wrong_file_path = os.path.join(os.path.dirname(__file__), "wrong_stocks.json")
        wrong_entry = {ticker: "This Ticker sell ops did not go well, go for manual debugging"}
        with open(wrong_file_path, "a") as f:
            f.write(json.dumps(wrong_entry) + "\n")
        #raise ValueError(f"Not enough shares to sell for ticker {ticker}. Requested: {requested_shares}")
    # Write the updated stocks back to the file, IF the sell succeed 
    with open(file_path, "w") as f:
        json.dump(stocks, f, indent=4)
        

    return total_amount


def update_invst_amounts(transaction_id, bought_shares, ticker, price, date, is_option=None,file_path=None,db=False):

    """
    Write to a JSON file to track stock purchases for later selling.

    Args:
        bought_shares (float): Number of shares bought.
        ticker (str): Ticker symbol.
        price (float or str): Per-share price (used to construct unique lot keys).
        date (str): ISO-format date of purchase (e.g., '2025-04-15').
        transaction_id (str): Unique transaction ID to ensure idempotency.
        file_path (str): Path to stocks.json file. Defaults to local directory.
    """
    from datetime import datetime
    base_path = os.path.dirname(__file__)
    if file_path is None:
        file_path = os.path.join(base_path, "stocks.json")
    if db:
        file_path = os.path.join(base_path, "stocks_db.json")  

        
    date = datetime.fromisoformat(date).strftime("%Y-%m-%d")
    unique_key = f"{price}_{date}_{transaction_id}"  
    # add marker if the investment is for an option contract 
    if is_option: 
        unique_key += "_option"
    # I will hard code some transactions that were USD stocks, but bought using CAD in the period 2024-07-22 to 2024-08-23
    if ticker == 'SYM' and unique_key == '31.9094_2024-08-23_810bf567-b9a4-4320-9546-e259b4362059':
        unique_key = '23.1625_2024-08-23'
    if ticker == 'COUR' and unique_key == '10.145_2024-07-22_80f857d7-666f-492f-8e2b-7e78cf786f84':
        unique_key = '7.228_2024-07-22'
    if ticker == 'COUR' and unique_key == '10.3745_2024-07-25_8e998a0d-93f1-4f4f-904a-bf3745527ba2':
        unique_key = '7.3661_2024-07-25'
    if ticker == 'CRWD' and unique_key == '371.28_2024-07-23_f1436e70-f50f-4206-9f2b-abad1772486c':
        unique_key = '264.542_2024-07-23'
    if ticker == 'MSFT' and unique_key == '598.51_2024-07-26_8113876e-7c03-452f-bda5-b69af9c44a80':
        unique_key = '424.405_2024-07-26'
    if ticker == 'ALB.TO' and transaction_id == '06500337-1916-4080-ad75-34f5e51215c4':
        ticker = 'ALB'
    

    try:
        with open(file_path, "r") as f:
            stocks = json.load(f)
        if ticker in stocks:
           
            if unique_key in stocks[ticker]:
                return # Already recorded this transaction
            else:
                stocks[ticker][unique_key] = bought_shares
        else:
            stocks[ticker] = {unique_key: bought_shares}

    except (FileNotFoundError, json.JSONDecodeError):
        stocks = {ticker: {unique_key: bought_shares}}

    with open(file_path, "w") as f:
        json.dump(stocks, f, indent=4)


def find_all_transcription_types(start_date="2024-07-01", end_date="2026-03-19"):
    from .snaptrade_api import get_transactions_for_user
    import json
    transactions = get_transactions_for_user(start_date=start_date, end_date=end_date)
    transactions_dict = {} 
    lst_of_transactions = []
    for transaction in transactions:
        if transaction['type'] == 'TAX':
            
            lst_of_transactions.append(transaction)
            transactions_dict[transaction['type']] = transaction['description']
    print(transactions_dict, lst_of_transactions)
    return transactions_dict, lst_of_transactions 

def mark_transaction_as_processed(transaction_id, db=False):
    if db:
        return

    import os, json
    base_path = os.path.dirname(__file__)
    tx_log_path = os.path.join(base_path, "processed_transactions.json")

    try:
        with open(tx_log_path, "r") as f:
            processed = set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        processed = set()

    if transaction_id not in processed:
        processed.add(transaction_id)
        with open(tx_log_path, "w") as f:
            json.dump(list(processed), f, indent=2)


def was_transaction_processed(transaction_id, db=False):
    if db:
        from dashboard.models import Transaction

        return Transaction.objects.filter(
            transaction_id=transaction_id,
            accounting_processed_at__isnull=False,
        ).exists()

    import os, json
    base_path = os.path.dirname(__file__)
    tx_log_path = os.path.join(base_path, "processed_transactions.json")

    try:
        with open(tx_log_path, "r") as f:
            processed = set(json.load(f))
        return transaction_id in processed
    except (FileNotFoundError, json.JSONDecodeError):
        return False


#resp = find_all_transcription_types()
#print(resp)



import os
import json

def find_credited_invst_amount_options(ticker, file_path=None, db=False):
    """
    Calculates the total credited amount when an option contract expires and update the value to zero after processing.

    Args:
        ticker (str): The stock symbol.
        file_path (str, optional): Path to the stocks JSON file. If not provided, defaults to 'stocks.json'
                                   in the same directory as this script.

    Returns:
        float: Total amount credited based on each share option premiuim * number of share (contracts * 100)

    Raises:
        FileNotFoundError: If the specified JSON file doesn't exist.
        
    """
    base_path = os.path.dirname(__file__)
    if file_path is None:
        file_path = os.path.join(base_path, "stocks.json")
    if db:
        file_path = os.path.join(base_path, "stocks_db.json")                                                                                               
        
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} does not exist.")

    with open(file_path, "r") as f:
        stocks = json.load(f)

    total_amount = 0
    for price_date_option, shares in stocks.get(ticker, {}).items():
        #Either not an option or it has expired before!
        if (not price_date_option.endswith("_option")) or stocks[ticker][price_date_option] == 0:
            continue

        else:
            premium = float(price_date_option.split("_", 1)[0])
            total_amount += premium * float(shares)
            stocks[ticker][price_date_option] = 0
            break

        

    # Write the updated stocks back to the file
    with open(file_path, "w") as f:
        json.dump(stocks, f, indent=4)
        

    return total_amount





def _to_decimal(value):
    from decimal import Decimal, InvalidOperation

    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0")


def _to_date(value):
    from datetime import datetime

    if hasattr(value, "date"):
        return value.date()
    if isinstance(value, str):
        if value.endswith("Z"):
            value = value.replace("Z", "+00:00")
        return datetime.fromisoformat(value).date()
    return value


def _normalize_lot_price(transaction_id, ticker, price, date):
    date_value = _to_date(date)
    unique_key = f"{price}_{date_value}_{transaction_id}"

    # Match the historical JSON lot overrides while the DB helpers are split out.
    overrides = {
        ("SYM", "31.9094_2024-08-23_810bf567-b9a4-4320-9546-e259b4362059"): "23.1625",
        ("COUR", "10.145_2024-07-22_80f857d7-666f-492f-8e2b-7e78cf786f84"): "7.228",
        ("COUR", "10.3745_2024-07-25_8e998a0d-93f1-4f4f-904a-bf3745527ba2"): "7.3661",
        ("CRWD", "371.28_2024-07-23_f1436e70-f50f-4206-9f2b-abad1772486c"): "264.542",
        ("MSFT", "598.51_2024-07-26_8113876e-7c03-452f-bda5-b69af9c44a80"): "424.405",
    }
    return _to_decimal(overrides.get((ticker, unique_key), price))


def _normalize_lot_currency(transaction_id, ticker, currency):
    usd_lot_overrides = {
        ("SYM", "810bf567-b9a4-4320-9546-e259b4362059"),
        ("COUR", "80f857d7-666f-492f-8e2b-7e78cf786f84"),
        ("COUR", "8e998a0d-93f1-4f4f-904a-bf3745527ba2"),
        ("CRWD", "f1436e70-f50f-4206-9f2b-abad1772486c"),
        ("MSFT", "8113876e-7c03-452f-bda5-b69af9c44a80"),
    }
    if (ticker, transaction_id) in usd_lot_overrides:
        return "USD"
    return currency


def _normalize_lot_ticker(transaction_id, ticker):
    ticker_overrides = {
        ("ALB.TO", "06500337-1916-4080-ad75-34f5e51215c4"): "ALB",
    }
    return ticker_overrides.get((ticker, transaction_id), ticker)


def update_invst_amounts_db(
    transaction_id,
    bought_shares,
    ticker,
    price,
    date,
    is_option=None,
    currency="USD",
):
    from dashboard.models import InvestmentLot, Transaction

    transaction = Transaction.objects.get(transaction_id=transaction_id)
    quantity = _to_decimal(bought_shares)
    acquired_date = _to_date(date)
    normalized_price = _normalize_lot_price(transaction_id, ticker, price, acquired_date)
    normalized_currency = _normalize_lot_currency(transaction_id, ticker, currency)
    normalized_ticker = _normalize_lot_ticker(transaction_id, ticker)

    lot, created = InvestmentLot.objects.get_or_create(
        transaction=transaction,
        symbol=normalized_ticker,
        is_option=bool(is_option),
        defaults={
            "currency": normalized_currency,
            "price": normalized_price,
            "quantity_original": quantity,
            "quantity_remaining": quantity,
            "acquired_date": acquired_date,
        },
    )
    return lot


def find_credited_invst_amount_db(sold_shares, ticker, currency=None, is_option=False):
    from django.db import transaction
    from dashboard.models import InvestmentLot

    remaining_to_sell = _to_decimal(sold_shares)
    total_amount = _to_decimal("0")

    lots = InvestmentLot.objects.select_for_update().filter(
        symbol=ticker,
        is_option=bool(is_option),
        quantity_remaining__gt=0,
    )
    if currency:
        lots = lots.filter(currency=currency)

    with transaction.atomic():
        for lot in lots.order_by("acquired_date", "id"):
            if remaining_to_sell <= 0:
                break

            quantity_used = min(lot.quantity_remaining, remaining_to_sell)
            total_amount += quantity_used * lot.price
            lot.quantity_remaining -= quantity_used
            lot.save(update_fields=["quantity_remaining"])
            remaining_to_sell -= quantity_used

        if remaining_to_sell > 0:
            wrong_file_path = os.path.join(os.path.dirname(__file__), "wrong_stocks_db.json")
            wrong_entry = {ticker: "This Ticker sell ops did not go well, go for manual debugging"}
            with open(wrong_file_path, "a") as f:
                f.write(json.dumps(wrong_entry) + "\n")
            #raise ValueError(
            #    f"Not enough investment lots for {ticker}. "
            #    f"Remaining unfilled quantity: {remaining_to_sell}"
            #)

    return total_amount


def find_credited_invst_amount_options_db(ticker, currency=None):
    from django.db import transaction
    from dashboard.models import InvestmentLot

    lots = InvestmentLot.objects.select_for_update().filter(
        symbol=ticker,
        is_option=True,
        quantity_remaining__gt=0,
    )
    if currency:
        lots = lots.filter(currency=currency)

    with transaction.atomic():
        lot = lots.order_by("acquired_date", "id").first()
        if lot is None:
            raise ValueError(f"No open option lot found for {ticker}.")

        total_amount = lot.quantity_remaining * lot.price
        lot.quantity_remaining = _to_decimal("0")
        lot.save(update_fields=["quantity_remaining"])

    return total_amount
