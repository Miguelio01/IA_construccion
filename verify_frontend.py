from playwright.sync_api import sync_playwright

def verify_feature():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(record_video_dir="/tmp/video")
        page = context.new_page()

        try:
            page.goto("http://localhost:3000")
            page.wait_for_timeout(1000)

            # The page should show the default Next.js starter since we haven't mounted our UploadForm yet
            # But let's verify it loads successfully.
            page.screenshot(path="/tmp/verification.png")
            page.wait_for_timeout(500)
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    verify_feature()
