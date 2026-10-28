"""Open Baidu in a visible Chromium browser using Playwright."""

from playwright.sync_api import sync_playwright


def open_baidu_page() -> None:
    """Open Baidu and keep the browser open until Enter is pressed."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        try:
            page = browser.new_page()
            page.goto("https://www.baidu.com", wait_until="domcontentloaded")
            print(f"Opened {page.url} - {page.title()}")
            input("Press Enter to close the browser...")
        finally:
            browser.close()


if __name__ == "__main__":
    open_baidu_page()