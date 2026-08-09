
def deposit(transaction, db=False):
    from datetime import datetime
    from .helpers import mark_transaction_as_processed

    date = datetime.fromisoformat(transaction['settlement_date'].rstrip('Z')).date()
    amount = float(transaction['amount'])
    description = transaction['description']

    row1 = [str(date), "TFSA (CAD)", f"{amount:.2f}", "", f"{description} CAD"]
    row2 = [str(date), "Cash (CAD)", "", f"{amount:.2f}", f"{description} CAD"]
    mark_transaction_as_processed(transaction["id"], db=db)
    return row1, row2

def buy_usd_stock(transaction, db=False):
    from .helpers import update_invst_amounts, update_invst_amounts_db, mark_transaction_as_processed
    from datetime import datetime

    date = datetime.fromisoformat(transaction['settlement_date'].rstrip('Z')).date()
    amount = float(abs(transaction['amount']))
    symbol = transaction['symbol']['symbol']
    description = transaction['description']

    row1 = [str(date), "TFSA (USD)", "", f"{amount:.2f}", f"{description} USD"]
    row2 = [str(date), "Investment (USD)", f"{amount:.2f}", "", f"{description} USD"]
    if db:
        update_invst_amounts_db(
            transaction['id'],
            abs(transaction['units']),
            symbol,
            transaction['price'],
            transaction['settlement_date'],
            currency="USD",
        )
    else:
        update_invst_amounts(
            transaction['id'],
            abs(transaction['units']),
            symbol,
            transaction['price'],
            transaction['settlement_date'],
            db=db,
        )
    mark_transaction_as_processed(transaction["id"], db=db)

    return row1, row2


def sell_usd_stock(transaction, db=False):
    from .helpers import find_credited_invst_amount, find_credited_invst_amount_db
    from datetime import datetime
    from .helpers import mark_transaction_as_processed

    date = datetime.fromisoformat(transaction['settlement_date'].rstrip('Z')).date()
    debited_cash_amount = float(abs(transaction['amount']))
    symbol = transaction['symbol']['symbol']
    description = transaction['description']

    row1 = [str(date), "TFSA (USD)", f"{debited_cash_amount:.2f}", "", f"{description} USD"]
    if db:
        credited_invst_amount = find_credited_invst_amount_db(
            abs(transaction['units']), symbol, currency="USD"
        )
    else:
        credited_invst_amount = find_credited_invst_amount(
            abs(transaction['units']), symbol
        )
    credited_invst_amount = float(credited_invst_amount)
    row2 = [str(date), "Investment (USD)", "", f"{credited_invst_amount:.2f}", f"{description} USD"]

    realized_gain_loss = debited_cash_amount - credited_invst_amount
    account = "Realized Gain/Loss (USD)"
    if realized_gain_loss > 0:
        row3 = [str(date), account, "", f"{realized_gain_loss:.2f}", f"{description} USD"]
    else:
        row3 = [str(date), account, f"{abs(realized_gain_loss):.2f}", "", f"{description} USD"]

    mark_transaction_as_processed(transaction["id"], db=db)
    return row1, row2, row3

def buy_cad_stock(transaction, db=False):
    from .helpers import update_invst_amounts, update_invst_amounts_db, mark_transaction_as_processed
    from datetime import datetime

    date = datetime.fromisoformat(transaction['settlement_date'].rstrip('Z')).date()
    amount = float(abs(transaction['amount']))
    symbol = transaction['symbol']['symbol']
    description = transaction['description']

    row1 = [str(date), "TFSA (CAD)", "", f"{amount:.2f}", f"{description} CAD"]
    row2 = [str(date), "Investment (CAD)", f"{amount:.2f}", "", f"{description} CAD"]

    if db:
        update_invst_amounts_db(
            transaction['id'],
            abs(transaction['units']),
            symbol,
            transaction['price'],
            transaction['settlement_date'],
            currency="CAD",
        )
    else:
        update_invst_amounts(
            transaction['id'],
            abs(transaction['units']),
            symbol,
            transaction['price'],
            transaction['settlement_date'],
        )
    mark_transaction_as_processed(transaction["id"], db=db)

    return row1, row2


def sell_cad_stock(transaction, db=False):
    from .helpers import find_credited_invst_amount, find_credited_invst_amount_db
    from datetime import datetime
    from .helpers import mark_transaction_as_processed

    date = datetime.fromisoformat(transaction['settlement_date'].rstrip('Z')).date()
    debited_cash_amount = float(abs(transaction['amount']))
    symbol = transaction['symbol']['symbol']
    description = transaction['description']

    row1 = [str(date), "TFSA (CAD)", f"{debited_cash_amount:.2f}", "", f"{description} CAD"]
    if db:
        credited_invst_amount = find_credited_invst_amount_db(
            abs(transaction['units']), symbol, currency="CAD"
        )
    else:
        credited_invst_amount = find_credited_invst_amount(
            abs(transaction['units']), symbol
        )
    credited_invst_amount = float(credited_invst_amount)
    row2 = [str(date), "Investment (CAD)", "", f"{credited_invst_amount:.2f}", f"{description} CAD"]

    realized_gain_loss = debited_cash_amount - credited_invst_amount
    account = "Realized Gain/Loss (CAD)"
    if realized_gain_loss > 0:
        row3 = [str(date), account, "", f"{realized_gain_loss:.2f}", f"{description} CAD"]
    else:
        row3 = [str(date), account, f"{abs(realized_gain_loss):.2f}", "", f"{description} CAD"]

    mark_transaction_as_processed(transaction["id"], db=db)
    return row1, row2, row3

def convert_cad_to_usd(transaction, db=False):
    from datetime import datetime
    from .helpers import mark_transaction_as_processed

    date = datetime.fromisoformat(transaction['settlement_date'].rstrip('Z')).date()
    amount = float(abs(transaction['amount']))
    description = transaction['description']

    row1 = [str(date), "TFSA (USD)", f"{amount}", "", description]
    row2 = [str(date), "TFSA (CAD)", "", "", description]
    row3 = [str(date), "Currency Conversion Expense (CAD)", "", "", description]
    mark_transaction_as_processed(transaction["id"], db=db)
    return row1, row2, row3

def fee(transaction, db=False):
    from datetime import datetime
    from .helpers import mark_transaction_as_processed

    date = datetime.fromisoformat(transaction['settlement_date'].rstrip('Z')).date()
    amount = float(abs(transaction['amount']))
    description = transaction['description']

    row1 = [str(date), "TFSA (CAD)", "", f"{amount:.2f}", description]
    row2 = [str(date), "Fee Expense (CAD)", f"{amount:.2f}", "", description]
    mark_transaction_as_processed(transaction["id"], db=db)
    return row1, row2

def dividend(transaction, db=False):
    from datetime import datetime
    from .helpers import mark_transaction_as_processed

    date = datetime.fromisoformat(transaction['settlement_date'].rstrip('Z')).date()
    amount = float(abs(transaction['amount']))
    currency = transaction['currency']['code']
    description = transaction['description']

    tfsa_account = "TFSA (CAD)" if currency == "CAD" else "TFSA (USD)"
    income_account = "Dividend Income (CAD)" if currency == "CAD" else "Dividend Income (USD)"

    row1 = [str(date), tfsa_account, f"{amount:.2f}", "", description]
    row2 = [str(date), income_account, "", f"{amount:.2f}", description]
    mark_transaction_as_processed(transaction["id"], db=db)
    return row1, row2

def tax(transaction, db=False):
    from datetime import datetime
    from .helpers import mark_transaction_as_processed

    date = datetime.fromisoformat(transaction['settlement_date'].rstrip('Z')).date()
    amount = float(abs(transaction['amount']))
    description = transaction['description']
    symbol_description = transaction['symbol']['description']

    row1 = [str(date), "TFSA (USD)", "", f"{amount:.2f}", description]
    row2 = [str(date), "Tax Expense (USD)", f"{amount:.2f}", "", f"{description}({symbol_description})"]
    mark_transaction_as_processed(transaction["id"], db=db)
    return row1, row2




def buy_usd_put_option(transaction, db=False):
    """
    Handle a BUY for one or more PUT contracts settled in USD.
    Produces two journal rows identical to buy_usd_stock(), except that the
    description becomes:
        "Bought <N> PUT option for <UNDERLYING> at <STRIKE>"
    """
    from datetime import datetime
    from .helpers import (
        update_invst_amounts,
        update_invst_amounts_db,
        mark_transaction_as_processed,
    )

    date        = datetime.fromisoformat(transaction["settlement_date"].rstrip("Z")).date()
    amount      = float(abs(transaction["amount"]))          # premium paid (same as stock logic)
    contracts   = int(abs(transaction["units"])) *100             # each contract is 100 share 
    underlying  = transaction["symbol"]["symbol"]             # e.g. "UAMY"
    strike      = transaction["option_symbol"]["strike_price"]
    option_tkr  = transaction["symbol"]["symbol"]      

    # --- narrative --------------------------------------------------------
    description = f"Bought {contracts} PUT option for {underlying} at {strike}"

    # --- journal rows -----------------------------------------------------
    row1 = [str(date), "TFSA (USD)", "",           f"{amount:.2f}", f"{description} USD"]
    row2 = [str(date), "Investment (USD)", f"{amount:.2f}", "",         f"{description} USD"]

    if db:
        update_invst_amounts_db(
            transaction["id"],
            contracts,
            option_tkr,
            transaction["price"],
            transaction["settlement_date"],
            is_option=True,
            currency="USD",
        )
    else:
        update_invst_amounts(
            transaction["id"],
            contracts,
            option_tkr,
            transaction["price"],
            transaction["settlement_date"],
            is_option=True,
        )
    mark_transaction_as_processed(transaction["id"], db=db)
    return row1, row2



def buy_usd_call_option(transaction, db=False):
    """
    Buy one or more CALL contracts settled in USD.
    """
    from datetime import datetime
    from .helpers import update_invst_amounts, update_invst_amounts_db, mark_transaction_as_processed

    date       = datetime.fromisoformat(transaction["settlement_date"].rstrip("Z")).date()
    amount     = float(abs(transaction["amount"]))
    contracts  = int(abs(transaction["units"])) * 100          # 1 contract = 100 shares
    symbol     = transaction["symbol"]["symbol"]               # underlying ticker
    strike     = transaction["option_symbol"]["strike_price"]

    descr = f"Bought {contracts} CALL option{'s' if contracts!=100 else ''} for {symbol} at {strike}"

    row1 = [str(date), "TFSA (USD)", "", f"{amount:.2f}", f"{descr} USD"]
    row2 = [str(date), "Investment (USD)", f"{amount:.2f}", "", f"{descr} USD"]

    if db:
        update_invst_amounts_db(
            transaction["id"],
            contracts,
            symbol,
            transaction["price"],
            transaction["settlement_date"],
            is_option=True,
            currency="USD",
        )
    else:
        update_invst_amounts(
            transaction["id"],
            contracts,
            symbol,
            transaction["price"],
            transaction["settlement_date"],
            is_option=True,
        )
    mark_transaction_as_processed(transaction["id"], db=db)
    return row1, row2


def buy_cad_put_option(transaction, db=False):
    """
    Buy PUT contracts settled in CAD.
    """
    from datetime import datetime
    from .helpers import update_invst_amounts, update_invst_amounts_db, mark_transaction_as_processed

    date       = datetime.fromisoformat(transaction["settlement_date"].rstrip("Z")).date()
    amount     = float(abs(transaction["amount"]))
    contracts  = int(abs(transaction["units"])) * 100
    symbol     = transaction["symbol"]["symbol"]
    strike     = transaction["option_symbol"]["strike_price"]

    descr = f"Bought {contracts} PUT option{'s' if contracts!=100 else ''} for {symbol} at {strike}"

    row1 = [str(date), "TFSA (CAD)", "", f"{amount:.2f}", f"{descr} CAD"]
    row2 = [str(date), "Investment (CAD)", f"{amount:.2f}", "", f"{descr} CAD"]

    if db:
        update_invst_amounts_db(
            transaction["id"],
            contracts,
            symbol,
            transaction["price"],
            transaction["settlement_date"],
            is_option=True,
            currency="CAD",
        )
    else:
        update_invst_amounts(
            transaction["id"],
            contracts,
            symbol,
            transaction["price"],
            transaction["settlement_date"],
            is_option=True,
        )
    mark_transaction_as_processed(transaction["id"], db=db)
    return row1, row2


def buy_cad_call_option(transaction, db=False):
    """
    Buy CALL contracts settled in CAD.
    """
    from datetime import datetime
    from .helpers import update_invst_amounts, update_invst_amounts_db, mark_transaction_as_processed

    date       = datetime.fromisoformat(transaction["settlement_date"].rstrip("Z")).date()
    amount     = float(abs(transaction["amount"]))
    contracts  = int(abs(transaction["units"])) * 100
    symbol     = transaction["symbol"]["symbol"]
    strike     = transaction["option_symbol"]["strike_price"]

    descr = f"Bought {contracts} CALL option{'s' if contracts!=100 else ''} for {symbol} at {strike}"

    row1 = [str(date), "TFSA (CAD)", "", f"{amount:.2f}", f"{descr} CAD"]
    row2 = [str(date), "Investment (CAD)", f"{amount:.2f}", "", f"{descr} CAD"]

    if db:
        update_invst_amounts_db(
            transaction["id"],
            contracts,
            symbol,
            transaction["price"],
            transaction["settlement_date"],
            is_option=True,
            currency="CAD",
        )
    else:
        update_invst_amounts(
            transaction["id"],
            contracts,
            symbol,
            transaction["price"],
            transaction["settlement_date"],
            is_option=True,
        )
    mark_transaction_as_processed(transaction["id"], db=db)
    return row1, row2


def option_expire(transaction, db=False):

    from .helpers import find_credited_invst_amount_options, find_credited_invst_amount_options_db
    from datetime import datetime
    from .helpers import mark_transaction_as_processed


    date = datetime.fromisoformat(transaction['settlement_date'].rstrip('Z')).date()
    symbol = transaction['symbol']['symbol']
    currency = transaction["currency"]["code"]
    description = f"{transaction['description']}_{symbol}"
    if db:
        premium_paid = find_credited_invst_amount_options_db(symbol, currency=currency)
    else:
        premium_paid = find_credited_invst_amount_options(symbol)
    premium_paid = float(premium_paid)

    # Record the expired option premium as a debit in the realized gain/loss account
    account = f"Realized Gain/Loss ({currency})"
    row1 = [str(date), account, f"{premium_paid:.2f}", "", f"{description}"]
    row2 = [str(date), f"Investment ({currency})", "", f"{premium_paid:.2f}", f"{description}"]

    mark_transaction_as_processed(transaction["id"], db=db)
    return row1, row2








def _sell_usd_option_common(transaction, call_or_put, db=False):
    from datetime import datetime
    from .helpers import find_credited_invst_amount, find_credited_invst_amount_db, mark_transaction_as_processed

    date = datetime.fromisoformat(transaction["settlement_date"].rstrip("Z")).date()
    cash_inflow = float(abs(transaction["amount"]))
    contracts = int(abs(transaction["units"])) * 100
    symbol = transaction["symbol"]["symbol"]
    strike = transaction["option_symbol"]["strike_price"]
    description = (
        f"Sold {contracts} {call_or_put} option"
        f"{'s' if contracts != 100 else ''} for {symbol} at {strike}"
    )

    row1 = [str(date), "TFSA (USD)", f"{cash_inflow:.2f}", "", f"{description} USD"]
    if db:
        cost_basis = find_credited_invst_amount_db(
            contracts, symbol, currency="USD", is_option=True
        )
    else:
        cost_basis = find_credited_invst_amount(contracts, symbol, is_option=True)
    cost_basis = float(cost_basis)
    row2 = [str(date), "Investment (USD)", "", f"{cost_basis:.2f}", f"{description} USD"]

    realized_gain_loss = cash_inflow - cost_basis
    account = "Realized Gain/Loss (USD)"
    if realized_gain_loss > 0:
        row3 = [str(date), account, "", f"{realized_gain_loss:.2f}", f"{description} USD"]
    else:
        row3 = [str(date), account, f"{abs(realized_gain_loss):.2f}", "", f"{description} USD"]

    mark_transaction_as_processed(transaction["id"], db=db)
    return row1, row2, row3


def sell_usd_put_option(transaction, db=False):
    return _sell_usd_option_common(transaction, "PUT", db=db)


def sell_usd_call_option(transaction, db=False):
    return _sell_usd_option_common(transaction, "CALL", db=db)


#
#def sell_cad_put_option(transaction):
#    return _sell_option_common(transaction, "CAD", "PUT")
#
#
#def sell_cad_call_option(transaction):
#    return _sell_option_common(transaction, "CAD", "CALL")
#
