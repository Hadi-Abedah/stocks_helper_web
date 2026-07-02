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

    # Require an authenticated portfolios-page marker. The old check returned
    # true for the URL alone, which can misclassify a signed-out Yahoo shell.
    authenticated_markers = [
        selectors.ALL_PORTFOLIOS_TEXT,
        "Portfolio Name",
        selectors.CREATE_NEW_PORTFOLIO_BUTTON_NAME,
    ]

    for text in authenticated_markers:
        try:
            page.get_by_text(text, exact=True).first.wait_for(timeout=5000)
            return True
        except Exception:
            pass

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
