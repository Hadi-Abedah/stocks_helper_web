from __future__ import annotations

from pathlib import Path

import pytest
from playwright.sync_api import sync_playwright

from stocks_helper.alerts.yahoo_portfolio_sync.auth import looks_logged_in
from stocks_helper.alerts.yahoo_portfolio_sync.schemas import YahooPortfolioConfig


def _test_config() -> YahooPortfolioConfig:
    return YahooPortfolioConfig(
        base_url="https://finance.yahoo.com",
        login_url="https://login.yahoo.com/",
        portfolio_url="https://finance.yahoo.com/portfolios",
        email="",
        password="",
        state_file=Path(__file__).resolve().parents[1] / ".yahoo_state.json",
        headless=True,
        slow_mo_ms=0,
        timeout_ms=20_000,
    )


def test_saved_yahoo_session_is_logged_in() -> None:
    config = _test_config()

    if not config.state_file.exists():
        pytest.skip(f"Missing saved Yahoo auth state: {config.state_file}")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(storage_state=str(config.state_file))
        page = context.new_page()

        try:
            assert looks_logged_in(page)
        finally:
            browser.close()
