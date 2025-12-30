from playwright.sync_api import sync_playwright, expect
import os

def run():
    with sync_playwright() as p:
        # Define a mobile device to emulate
        pixel_5 = p.devices['Pixel 5']
        browser = p.chromium.launch(headless=True)

        # Create a context with the emulated device
        context = browser.new_context(**pixel_5)
        page = context.new_page()

        try:
            page.goto("http://localhost:8000")
            print("Successfully navigated to the page on a mobile device.")

            # Upload a receipt and verify the result
            file_path = "sample_receipt2.png"
            page.set_input_files('input[type="file"]', file_path)
            page.click('button[type="submit"]')
            print("Uploaded a new receipt.")

            # Wait for the receipt list to be updated
            # A more robust way to wait is to expect an element to be visible
            expect(page.locator(".receipt-item").first).to_be_visible(timeout=10000)
            print("Receipt list updated.")

            # Create verification directory if it doesn't exist
            os.makedirs("verification", exist_ok=True)

            # Take a screenshot for verification
            screenshot_path = "verification/verification_mobile.png"
            page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")

        except Exception as e:
            print(f"An error occurred: {e}")
            os.makedirs("verification", exist_ok=True)
            page.screenshot(path="verification/error_mobile.png")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
