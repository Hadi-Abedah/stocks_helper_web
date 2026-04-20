from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from .schemas import YahooPortfolioConfig

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from .schemas import YahooPortfolioConfig
from . import selectors


@dataclass
class YahooClient:
    playwright: Playwright
    browser: Browser
    context: BrowserContext
    page: Page

    def close(self) -> None:
        self.context.close()
        self.browser.close()
        self.playwright.stop()


def build_client(config: YahooPortfolioConfig) -> YahooClient:
    playwright = sync_playwright().start()

    browser = playwright.chromium.launch(
        headless=config.headless,
        slow_mo=config.slow_mo_ms,
    )

    context_kwargs = {
        "viewport": {"width": 1400, "height": 1000},
    }

    if config.state_file.exists():
        print(f"[INFO] Loading saved auth state from: {config.state_file}")
        context_kwargs["storage_state"] = str(config.state_file) #type: ignore

    context = browser.new_context(**context_kwargs) #type: ignore
    page = context.new_page()
    page.set_default_timeout(config.timeout_ms)

    return YahooClient(
        playwright=playwright,
        browser=browser,
        context=context,
        page=page,
    )


# portfolio 



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


def choose_portfolio_from_menu(page: Page, portfolio_name: str) -> None:
    """
    Clicks a portfolio name from the open My Portfolio dropdown.

    From your screenshot, the visible portfolio name text is inside:
    <span class="item-content ...">my holdings</span>

    So text-based locator is a good first choice.
    """
    item = page.get_by_text(portfolio_name, exact=True).first
    item.click()


def open_portfolio(page: Page, portfolio_name: str) -> None:
    click_my_portfolio_menu(page)
    choose_portfolio_from_menu(page, portfolio_name)
    page.wait_for_url("**/portfolio/**", timeout=15_000)
    page.get_by_role("button", name=selectors.ADD_TICKERS_BUTTON_NAME).wait_for(timeout=10_000)
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