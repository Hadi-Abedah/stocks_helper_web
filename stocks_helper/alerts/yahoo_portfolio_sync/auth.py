from __future__ import annotations

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from .schemas import YahooPortfolioConfig
from . import selectors


def _try_fill_first_label(page: Page, labels: list[str], value: str) -> bool:
    for label in labels:
        locator = page.get_by_label(label)
        try:
            if locator.count() > 0:
                locator.first.fill(value)
                return True
        except Exception:
            continue
    return False


def _try_click_button_by_name(page: Page, names: list[str]) -> bool:
    for name in names:
        locator = page.get_by_role("button", name=name)
        try:
            if locator.count() > 0:
                locator.first.click()
                return True
        except Exception:
            continue
    return False


def dismiss_optional_dialogs(page: Page) -> None:
    for name in selectors.OPTIONAL_BUTTON_NAMES:
        try:
            locator = page.get_by_role("button", name=name)
            if locator.count() > 0:
                locator.first.click(timeout=2000)
        except Exception:
            pass


def looks_logged_in(page: Page) -> bool:
    """
    Heuristic check only.
    We do NOT depend on one exact text node because Yahoo UI is dynamic.
    """
    try:
        page.goto("https://finance.yahoo.com/portfolios", wait_until="domcontentloaded")
    except Exception:
        return False

    current_url = page.url.lower()

    # Strong negative signal
    if "login.yahoo.com" in current_url:
        return False

    # Strong positive signal:
    # We reached Yahoo Finance and were not bounced to login.
    if "finance.yahoo.com" in current_url:
        # Try a few optional UI checks, but do not require all of them.
        possible_texts = [
            "My Portfolio",
            "Portfolio",
            "My Portfolios",
            "Summary",
        ]

        for text in possible_texts:
            try:
                page.get_by_text(text).first.wait_for(timeout=3000)
                return True
            except Exception:
                pass

        # Even if text did not appear, being on finance.yahoo.com/portfolios
        # without redirecting to login is already a useful signal.
        if "/portfolios" in current_url:
            return True

        return True

    return False


def login(page: Page, config: YahooPortfolioConfig) -> None:
    page.goto(config.login_url, wait_until="domcontentloaded")
    dismiss_optional_dialogs(page)

    email_filled = _try_fill_first_label(page, selectors.EMAIL_INPUT_LABELS, config.email)
    if not email_filled:
        raise RuntimeError("Could not find Yahoo email/username input.")

    clicked_next = _try_click_button_by_name(page, selectors.NEXT_BUTTON_NAMES)
    if not clicked_next:
        # Sometimes Enter may work if button locator changes
        page.keyboard.press("Enter")

    try:
        page.wait_for_load_state("networkidle", timeout=10_000)
    except PlaywrightTimeoutError:
        pass

    password_filled = _try_fill_first_label(page, selectors.PASSWORD_INPUT_LABELS, config.password)
    if not password_filled:
        raise RuntimeError("Could not find Yahoo password input.")

    clicked_sign_in = _try_click_button_by_name(page, selectors.SIGN_IN_BUTTON_NAMES)
    if not clicked_sign_in:
        page.keyboard.press("Enter")

    try:
        page.wait_for_load_state("networkidle", timeout=15_000)
    except PlaywrightTimeoutError:
        pass

    dismiss_optional_dialogs(page)


def ensure_logged_in(page: Page, config: YahooPortfolioConfig, context) -> None:
    if looks_logged_in(page):
        print("[INFO] Existing saved session is already logged in.")
        return

    try:
        login(page, config)
    except Exception as exc:
        print(f"[WARN] Automatic login step failed: {exc}")

    # If auto login did not finish, allow manual completion.
    if not looks_logged_in(page):
        print("[INFO] Automatic login did not fully complete.")
        print("[INFO] Browser will pause now.")
        print("[INFO] Please finish Yahoo login manually in the browser.")
        print("[INFO] When you reach the logged-in Finance/Portfolio page, click Resume in Playwright Inspector.")

        page.pause()

    if not looks_logged_in(page):
        raise RuntimeError(
            "Manual login fallback finished, but session still does not look authenticated."
        )

    context.storage_state(path=str(config.state_file))
    print(f"[INFO] Saved authenticated state to: {config.state_file}")





def bootstrap_manual_login(page: Page, config: YahooPortfolioConfig, context) -> None:
    page.goto(config.login_url, wait_until="domcontentloaded")

    print("[INFO] Manual Yahoo login bootstrap started.")
    print("[INFO] Please complete login manually.")
    print("[INFO] After you reach Yahoo Finance while logged in, click Resume.")

    page.pause()

    if not looks_logged_in(page):
        raise RuntimeError(
            "Manual login completed, but the session still does not appear logged in."
        )

    context.storage_state(path=str(config.state_file))
    print(f"[INFO] Saved authenticated state to: {config.state_file}")