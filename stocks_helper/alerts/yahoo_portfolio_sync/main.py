from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

from .actions import (
    open_portfolios_page,
    open_portfolio,
    click_add_tickers,
    fill_ticker_lookup,
    select_ticker_result,
    confirm_add_ticker,
)
from .auth import ensure_logged_in
from .client import build_client
from .schemas import load_config


def main() -> None:
    env_path = Path(__file__).resolve().parent / ".env"
    load_dotenv(env_path)

    config = load_config()
    client = build_client(config)

    try:
        ensure_logged_in(client.page, config, client.context)
        open_portfolios_page(client.page, config)
        open_portfolio(client.page, "my holdings")
        click_add_tickers(client.page)

        fill_ticker_lookup(client.page, "CLBT")
        select_ticker_result(client.page, "CLBT")
        confirm_add_ticker(client.page)

        print("[INFO] Add-ticker flow completed.")
        #client.page.pause()

    finally:
        client.close()


if __name__ == "__main__":
    main()