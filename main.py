from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    #browser = p.chromium.launch(headless=False)
    browser = p.firefox.launch(headless=False)
    page = browser.new_page()
    page.goto("https://google.com")
    page.screenshot(path="google.png")
    browser.close()