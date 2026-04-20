

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class YahooPortfolioConfig:
    base_url: str
    login_url: str
    portfolio_url: str
    email: str
    password: str
    state_file: Path
    headless: bool
    slow_mo_ms: int
    timeout_ms: int


def load_config() -> YahooPortfolioConfig:
    email = os.getenv("YAHOO_EMAIL", "").strip()
    password = os.getenv("YAHOO_PASSWORD", "").strip()

    if not email:
        raise ValueError("Missing YAHOO_EMAIL in .env")
    if not password:
        raise ValueError("Missing YAHOO_PASSWORD in .env")

    return YahooPortfolioConfig(
        base_url="https://finance.yahoo.com",
        login_url="https://login.yahoo.com/",
        portfolio_url="https://finance.yahoo.com/portfolios",
        email=email,
        password=password,
        state_file=Path(__file__).resolve().parent / ".yahoo_state.json",
        headless=False,     # start with False for debugging
        slow_mo_ms=150,     # slow actions a bit so you can watch
        timeout_ms=20_000,
    )