from playwright.sync_api import sync_playwright
import pandas as pd
import time
from pathlib import Path
from datetime import datetime

def auto_cleanup(folder: Path, prefix="amazon_results_", keep=5):
    files = sorted(
        [f for f in folder.glob(f"{prefix}*.xlsx") if f.is_file()],
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )

    if len(files) <= keep:
        return

    for f in files[keep:]:
        try:
            f.unlink()
            print(f"🗑️ Deleted old file: {f.name}")
        except Exception as e:
            print(f"❌ Could not delete {f}: {e}")


def scrape_amazon(product, limit=500):

    # ------------------------------
    # 1. Professional Path Handling
    # ------------------------------
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    file_name = f"amazon_results_{timestamp}.xlsx"

    BASE_DIR = Path(__file__).resolve().parent       # scraping folder
    DATA_DIR = BASE_DIR / "data"
    DATA_DIR.mkdir(exist_ok=True)                   # auto-create folder
    OUTPUT_FILE = DATA_DIR / file_name  # final excel path


    items = []
    page_number = 1

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        )

        url = f"https://www.amazon.com/s?k={product.replace(' ', '+')}"
        page.goto(url, timeout=60000)

        while len(items) < limit:
            page.wait_for_selector("div.s-card-container", timeout=60000)

            titles = page.locator("h2.a-size-medium span").all_text_contents()

            for t in titles:
                if len(items) >= limit:
                    break
                items.append({
                    "Product Title": t.strip(),
                    "Page": page_number
                })

            print(f"Page {page_number}: Total Collected — {len(items)}")

            # ------------------------------
            # 2. Better Next Page Handling
            # ------------------------------
            next_button = page.locator("a.s-pagination-next")
            if not next_button or not next_button.is_visible():
                print("No next page. Stopping.")
                break
            try:
                next_button.click()
            except:
                print("Next button click failed. Stopping.")
            
            page_number += 1
            time.sleep(2)  # allow next page to load

        browser.close()

    # Save to Excel
    df = pd.DataFrame(items)
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"\nSaved {len(items)} items to {OUTPUT_FILE}")

    # 🔥 Auto-clean old Excel files (keep last 5)
    auto_cleanup(DATA_DIR, keep=5)


scrape_amazon("laptop", limit=500)