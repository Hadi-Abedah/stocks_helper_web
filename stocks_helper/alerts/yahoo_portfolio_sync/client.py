from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal

from playwright.sync_api import Page, Locator, TimeoutError as PlaywrightTimeoutError


from .schemas import YahooPortfolioConfig, PortfolioName


AddTickerStatus = Literal["added", "already_present", "not_found", "other_error"]


@dataclass
class AddTickerResult:
    ticker: str
    status: AddTickerStatus


class YahooPortfolioClient:
    def __init__(self, page: Page, config: YahooPortfolioConfig) -> None:
        self.page = page
        self.config = config
        self.debug_screenshot_dir = Path(__file__).resolve().parent / "debug_screenshots"

    def _debug_screenshot_path(self, filename: str) -> str:
        self.debug_screenshot_dir.mkdir(exist_ok=True)
        return str(self.debug_screenshot_dir / filename)

    def open_portfolios_page(self) -> None:
        self.page.goto(self.config.portfolio_url, wait_until="domcontentloaded")

    def open_portfolio(self, portfolio_name: PortfolioName) -> None:
       if "login.yahoo.com" in self.page.url.lower():
           raise RuntimeError("Yahoo redirected to login; saved session is not authenticated.")

       try:
           if self.page.get_by_role("link", name="Sign in").is_visible(timeout=1000):
               raise RuntimeError("Yahoo Finance is showing a Sign in link; saved session is not authenticated.")
       except PlaywrightTimeoutError:
           pass

       self.page.get_by_text("Portfolio Name", exact=True).wait_for(timeout=60_000)

       portfolio_link = self.page.locator(
           f"a:visible:has-text('{portfolio_name}')"
       ).first

       portfolio_link.wait_for(state="visible", timeout=60_000)

       try:
           # Normal/original behavior
           portfolio_link.click(timeout=60_000)

       except PlaywrightTimeoutError:
           print("[WARN] Portfolio link click timed out. Falling back to direct href navigation.")
           print("Current URL before fallback:", self.page.url)

           href = portfolio_link.get_attribute("href")
           if href is None:
               self.page.screenshot(
                   path=self._debug_screenshot_path("yahoo_portfolio_click_timeout.png"),
                   full_page=True,
               )
               raise RuntimeError(f"Could not find portfolio href for {portfolio_name}")

           if href.startswith("/"):
               href = f"https://finance.yahoo.com{href}"

           print(f"[INFO] Opening portfolio directly: {href}")
           self.page.goto(href, wait_until="domcontentloaded", timeout=60_000)

       try:
           self.page.wait_for_url("**/portfolio/**", timeout=60_000)
           self.page.get_by_role("button", name="Add tickers").wait_for(timeout=60_000)

       except Exception:
           print("Did not reach expected portfolio page.")
           print("Current URL:", self.page.url)
           self.page.screenshot(
               path=self._debug_screenshot_path("yahoo_portfolio_debug.png"),
               full_page=True,
           )
           raise

    def click_add_tickers(self) -> None:
        add_button = self.page.get_by_role("button", name="Add tickers")
        add_button.wait_for(timeout=60_000)
    
        add_button.click(timeout=60_000, no_wait_after=True)
    
        self.page.get_by_role("alertdialog").wait_for(timeout=60_000)

    def get_add_ticker_dialog(self) -> Locator:
        dialog = self.page.get_by_role("alertdialog")
        dialog.wait_for(timeout=30_000)
        return dialog

    def fill_ticker_lookup(self, ticker: str) -> None:
        dialog = self.get_add_ticker_dialog()
        quote_input = dialog.get_by_placeholder("Quote Lookup")
        quote_input.wait_for(timeout=30_000)
        quote_input.fill(ticker)

    def select_ticker_result(self, ticker: str) -> AddTickerStatus:
        dialog = self.get_add_ticker_dialog()

        row = dialog.locator("li").filter(has_text=ticker).first

        try:
            row.wait_for(timeout=30_000)
        except PlaywrightTimeoutError:
            if dialog.get_by_text("No matching results found").is_visible():
                return "not_found"
            return "other_error"

        checkbox = row.locator("input[type='checkbox']")
        if checkbox.is_disabled():
            return "already_present"

        row.click()
        return "added"

    

    def confirm_add_ticker(self) -> None:
        dialog = self.get_add_ticker_dialog()
        add_button = dialog.get_by_role("button", name="Add ticker")
        add_button.wait_for(timeout=30_000)
        add_button.click()
        
    def close_add_ticker_dialog(self) -> None:
        dialog = self.get_add_ticker_dialog()
        dialog.get_by_role("button", name="Close").click()
        dialog.wait_for(state="hidden", timeout=30_000)

    def add_ticker_to_current_portfolio(self, ticker: str) -> AddTickerResult:
        self.click_add_tickers()
        self.fill_ticker_lookup(ticker)

        status = self.select_ticker_result(ticker)

        if status != "added":
            self.close_add_ticker_dialog()
            return AddTickerResult(ticker=ticker, status=status)

        self.confirm_add_ticker()
        return AddTickerResult(ticker=ticker, status="added")

    def add_ticker_to_portfolio(
        self,
        portfolio_name: PortfolioName,
        ticker: str,
    ) -> AddTickerResult:
        self.open_portfolios_page()
        self.open_portfolio(portfolio_name)
        return self.add_ticker_to_current_portfolio(ticker)

    def add_tickers_to_portfolio(
        self,
        portfolio_name: PortfolioName,
        tickers: Iterable[str],
    ) -> list[AddTickerResult]:
        self.open_portfolios_page()
        self.open_portfolio(portfolio_name)

        results: list[AddTickerResult] = []

        for ticker in tickers:
            try:
                result = self.add_ticker_to_current_portfolio(ticker)
                print(f"[INFO] {result.ticker}: {result.status}")
                results.append(result)
            except PlaywrightTimeoutError:
                print(f"[WARN] Timeout while adding {ticker}. Reopening portfolio and retrying once.")
                self.open_portfolios_page()
                self.open_portfolio(portfolio_name)
                result = self.add_ticker_to_current_portfolio(ticker)
                print(f"[INFO] {result.ticker}: {result.status} after retry")
                results.append(result)
        return results

    def read_portfolio_tickers(self, portfolio_name: PortfolioName) -> set[str]:
        self.open_portfolios_page()
        self.open_portfolio(portfolio_name)

        ticker_links = self.page.locator("table tbody tr td:first-child a[href^='/quote/']")
        ticker_links.first.wait_for(timeout=30_000)

        tickers: set[str] = set()
        for i in range(ticker_links.count()):
            ticker = ticker_links.nth(i).inner_text().strip().upper()
            if ticker:
                tickers.add(ticker)

        return tickers


######
#open page
#open portfolio
#for each ticker:
#    open modal
#    search ticker
#    select result or close modal
#    confirm add
