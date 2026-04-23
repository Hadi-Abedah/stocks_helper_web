from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

from playwright.sync_api import Page

from .schemas import YahooPortfolioConfig, PortfolioName


AddTickerStatus = Literal["added", "already_present"]


@dataclass
class AddTickerResult:
    ticker: str
    status: AddTickerStatus


class YahooPortfolioClient:
    def __init__(self, page: Page, config: YahooPortfolioConfig) -> None:
        self.page = page
        self.config = config

    def open_portfolios_page(self) -> None:
        self.page.goto(self.config.portfolio_url, wait_until="domcontentloaded")

    def open_portfolio(self, portfolio_name: PortfolioName) -> None:
        self.page.get_by_text("Portfolio Name", exact=True).wait_for(timeout=10_000)
        portfolio_link = self.page.locator(
            f"a:visible:has-text('{portfolio_name}')"
        ).first
        portfolio_link.click()
        self.page.wait_for_url("**/portfolio/**", timeout=15_000)
        self.page.get_by_role("button", name="Add tickers").wait_for(timeout=15_000)

    def click_add_tickers(self) -> None:
        self.page.get_by_role("button", name="Add tickers").click()

    def get_add_ticker_dialog(self):
        dialog = self.page.get_by_role("alertdialog")
        dialog.wait_for(timeout=10_000)
        return dialog

    def fill_ticker_lookup(self, ticker: str) -> None:
        dialog = self.get_add_ticker_dialog()
        quote_input = dialog.get_by_placeholder("Quote Lookup")
        quote_input.wait_for(timeout=10_000)
        quote_input.fill(ticker)

    def select_ticker_result(self, ticker: str) -> bool:
        dialog = self.get_add_ticker_dialog()
        row = dialog.locator("li").filter(has_text=ticker).first
        row.wait_for(timeout=10_000)

        checkbox = row.locator("input[type='checkbox']")
        if checkbox.is_disabled():
            return False

        row.click()
        return True

    def confirm_add_ticker(self) -> None:
        dialog = self.get_add_ticker_dialog()
        add_button = dialog.get_by_role("button", name="Add ticker")
        add_button.wait_for(timeout=10_000)
        add_button.click()

    def add_ticker_to_portfolio(
        self,
        portfolio_name: PortfolioName,
        ticker: str,
    ) -> AddTickerResult:
        self.open_portfolios_page()
        self.open_portfolio(portfolio_name)
        self.click_add_tickers()
        self.fill_ticker_lookup(ticker)

        if not self.select_ticker_result(ticker):
            return AddTickerResult(ticker=ticker, status="already_present")

        self.confirm_add_ticker()
        return AddTickerResult(ticker=ticker, status="added")

    def add_tickers_to_portfolio(
        self,
        portfolio_name: PortfolioName,
        tickers: Iterable[str],
    ) -> list[AddTickerResult]:
        self.open_portfolios_page()
        self.open_portfolio(portfolio_name)

        results: list[AddTickerResult] = []

        for ticker in tickers:
            self.click_add_tickers()
            self.fill_ticker_lookup(ticker)

            if not self.select_ticker_result(ticker):
                results.append(AddTickerResult(ticker=ticker, status="already_present"))
                continue

            self.confirm_add_ticker()
            results.append(AddTickerResult(ticker=ticker, status="added"))

        return results