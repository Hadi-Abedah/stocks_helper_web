#deprecated 
from __future__ import annotations

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from .schemas import YahooPortfolioConfig, PortfolioName
from . import selectors


def open_portfolios_page(page: Page, config: YahooPortfolioConfig) -> None:
    page.goto(config.portfolio_url, wait_until="domcontentloaded")


def debug_url(page: Page, label: str) -> None:
    print(f"[DEBUG] {label} URL: {page.url}")


def click_my_portfolio_menu(page: Page) -> None:
    """
    Opens the top-left 'My Portfolio' dropdown/menu.
    """
    trigger = page.get_by_text(selectors.MY_PORTFOLIO_TRIGGER_TEXT, exact=True).first
    trigger.click()


def choose_portfolio_from_menu(page: Page, portfolio_name: PortfolioName) -> None:
    """
    Clicks a portfolio name from the open My Portfolio dropdown.

    From your screenshot, the visible portfolio name text is inside:
    <span class="item-content ...">my holdings</span>

    So text-based locator is a good first choice.
    """
    item = page.get_by_text(portfolio_name, exact=True).first
    item.click()


def open_portfolio(page: Page, portfolio_name: str) -> None:
    """
    Open a portfolio from the portfolio list table on /portfolios.
    """

    page.get_by_text("Portfolio Name", exact=True).wait_for(timeout=10_000)

    portfolio_link = page.locator(f"a:visible:has-text('{portfolio_name}')").first
    portfolio_link.click()

    page.wait_for_url("**/portfolio/**", timeout=15_000)

    # Better success marker than portfolio name text:
    # this button exists on the portfolio detail page in your screenshot.
    page.get_by_role("button", name="Add tickers").wait_for(timeout=15_000)

    debug_url(page, f"Opened portfolio '{portfolio_name}'")


def click_add_tickers(page: Page) -> None:
    """
    Click the 'Add tickers' button inside a portfolio page.
    """
    add_button = page.get_by_role("button", name=selectors.ADD_TICKERS_BUTTON_NAME)
    add_button.click()

    # After clicking, a dialog / panel / form should appear.
    # We do not know the exact final markup yet, so for now we only confirm
    # the button was clickable and the page remains interactive.
    print("[INFO] Clicked 'Add tickers' button.")


def get_add_ticker_dialog(page):
    dialog = page.get_by_role("alertdialog")
    dialog.wait_for(timeout=10_000)
    return dialog


def fill_ticker_lookup(page: Page, ticker: str) -> None:
    dialog = get_add_ticker_dialog(page)

    quote_input = dialog.get_by_placeholder("Quote Lookup")
    quote_input.wait_for(timeout=10_000)
    quote_input.click()
    quote_input.fill(ticker)

    print(f"[INFO] Filled ticker lookup with: {ticker}")

def select_ticker_result(page: Page, ticker: str) -> bool:
    dialog = get_add_ticker_dialog(page)

    # Find the row that contains the ticker
    row = dialog.locator("li").filter(has_text=ticker).first
    row.wait_for(timeout=10_000)

    checkbox = row.locator("input[type='checkbox']")

    if checkbox.is_disabled():
        print(f"[INFO] Ticker already added (disabled): {ticker}")
        return False

    row.click()
    print(f"[INFO] Selected ticker result for: {ticker}")
    return True

def confirm_add_ticker(page: Page) -> None:
    dialog = get_add_ticker_dialog(page)

    add_button = dialog.get_by_role("button", name="Add ticker")
    add_button.wait_for(timeout=10_000)
    add_button.click()

    print("[INFO] Clicked final 'Add ticker' button.")