from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from stocks_helper.stock_actions.watch_list.main import read as watch_list_main
from .auth import ensure_logged_in
from .client import YahooPortfolioClient
from .schemas import load_config, PortfolioName



def _separate_cad_usd(tickers: list[str]) -> tuple[list[str], list[str]]:
    cad_tickers = []
    usd_tickers = []
    for ticker in tickers:
        if ticker.endswith(".TO"):
            cad_tickers.append(ticker)
        else:
            usd_tickers.append(ticker)
    return cad_tickers, usd_tickers


def _still_not_added_tickers(tickers: list[str], existing_tickers: set[str]) -> list[str]:
    return [ticker for ticker in tickers if ticker.upper() not in existing_tickers]


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
        context.on("page", lambda page: page.close())
        client = YahooPortfolioClient(page=page, config=config)
        tickers_to_add = watch_list_main()
        cad_tickers, usd_tickers = _separate_cad_usd(tickers_to_add)
        all_results = []
        # USD tickers go to "my holdings".
        if usd_tickers:
            portfolio: PortfolioName = "my holdings"
            existing_tickers = client.read_portfolio_tickers(portfolio)
            usd_tickers = _still_not_added_tickers(usd_tickers, existing_tickers)
            if usd_tickers:
                results = client.add_tickers_to_portfolio(
                    portfolio_name=portfolio,
                    tickers=usd_tickers,
                )
                all_results.extend(results)
            else:
                print(f"[INFO] No new tickers to add to {portfolio}.")

        # CAD tickers go to "cad".
        if cad_tickers:
            portfolio: PortfolioName = "cad"
            existing_tickers = client.read_portfolio_tickers(portfolio)
            cad_tickers = _still_not_added_tickers(cad_tickers, existing_tickers)
            if cad_tickers:
                results = client.add_tickers_to_portfolio(
                    portfolio_name=portfolio,
                    tickers=cad_tickers,
                )
                all_results.extend(results)
            else:
                print(f"[INFO] No new tickers to add to {portfolio}.")

        print("\n[RESULTS]")
        for result in all_results:
            print(f"{result.ticker}: {result.status}")

        browser.close()


if __name__ == "__main__":
    main()
