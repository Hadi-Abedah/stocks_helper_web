from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from .auth import ensure_logged_in
from .client import YahooPortfolioClient
from .schemas import load_config, PortfolioName

# Demo inputs for now
TICKERS = ["AKAN", "GME"]
PORTFOLIO: PortfolioName = "risky"


def main() -> None:
    env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(env_path)

    config = load_config()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        context = browser.new_context(
            storage_state=str(config.state_file) if config.state_file.exists() else None
        )
        page = context.new_page()

        ensure_logged_in(page, config, context)

        client = YahooPortfolioClient(page=page, config=config)
        results = client.add_tickers_to_portfolio(
            portfolio_name=PORTFOLIO,
            tickers=TICKERS,
        )

        print("\n[RESULTS]")
        for result in results:
            print(f"{result.ticker}: {result.status}")

        browser.close()


if __name__ == "__main__":
    main()