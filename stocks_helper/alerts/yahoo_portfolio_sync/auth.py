from __future__ import annotations

import re
from pathlib import Path

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


def _visible_with_timeout(locator, timeout_ms: int = 3000) -> bool:
    try:
        locator.first.wait_for(state="visible", timeout=timeout_ms)
        return True
    except Exception:
        return False


def _print_auth_debug_state(page: Page) -> None:
    screenshot_dir = Path(__file__).resolve().parent / "debug_screenshots"
    screenshot_dir.mkdir(exist_ok=True)
    screenshot_path = screenshot_dir / "auth_not_detected.png"

    print(f"[DEBUG] Auth check URL: {page.url}")
    try:
        print(f"[DEBUG] Auth check title: {page.title()}")
    except Exception:
        pass

    try:
        page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"[DEBUG] Saved auth debug screenshot: {screenshot_path}")
    except Exception as exc:
        print(f"[DEBUG] Could not save auth debug screenshot: {exc}")


# added by codex when I had login problem, probably not what I want, retest that later!
def continue_from_signed_out_step(page: Page) -> bool:
    try:
        signed_out = page.get_by_text("Signed out", exact=True)
        if signed_out.count() > 0:
            signed_out.first.click(timeout=5000)
            return True
    except Exception:
        pass
    return False


def looks_logged_in(page: Page) -> bool:
    """
    Check whether the saved browser state can reach the authenticated
    Yahoo Finance portfolios page.
    """
    try:
        page.goto("https://finance.yahoo.com/portfolios", wait_until="domcontentloaded")
        try:
            page.wait_for_load_state("networkidle", timeout=10_000)
        except PlaywrightTimeoutError:
            pass
    except Exception:
        return False

    current_url = page.url.lower()

    # Strong negative signals.
    if "login.yahoo.com" in current_url:
        return False

    try:
        if page.get_by_role("link", name="Sign in").is_visible(timeout=1000):
            return False
    except Exception:
        pass

    if "finance.yahoo.com" not in current_url:
        return False

    # Require an authenticated portfolio marker. Prefer role/link checks and
    # quote links over exact page text because Yahoo changes spacing/markup.
    authenticated_markers = [
        page.get_by_role(
            "link",
            name=re.compile(rf"^{re.escape(selectors.MY_PORTFOLIO_TRIGGER_TEXT)}$", re.I),
        ),
        page.get_by_role(
            "button",
            name=re.compile(rf"^{re.escape(selectors.MY_PORTFOLIO_TRIGGER_TEXT)}$", re.I),
        ),
        page.get_by_text(selectors.ALL_PORTFOLIOS_TEXT),
        page.get_by_text("Portfolio Name"),
        page.get_by_role("button", name=selectors.CREATE_NEW_PORTFOLIO_BUTTON_NAME),
        page.get_by_role("button", name=selectors.ADD_TICKERS_BUTTON_NAME),
        page.locator("table tbody tr td:first-child a[href^='/quote/']"),
    ]

    for marker in authenticated_markers:
        if _visible_with_timeout(marker, timeout_ms=5000):
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
# added by codex when I had login problem, probably not what I want, retest that later!
    continue_from_signed_out_step(page)
#####################3
    try:
        page.wait_for_load_state("networkidle", timeout=10_000)
    except PlaywrightTimeoutError:
        pass
# added by codex when I had login problem, probably not what I want, retest that later!
    continue_from_signed_out_step(page)
###########################################
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
        _print_auth_debug_state(page)
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
