from playwright.sync_api import sync_playwright, expect
import os

def run():
    with sync_playwright() as p:
        pixel_5 = p.devices['Pixel 5']
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(**pixel_5)
        page = context.new_page()

        try:
            page.goto("http://localhost:8000")
            print("Successfully navigated to the page on a mobile device.")

            # --- Test File Upload and Edit Workflow ---
            file_path = "sample_receipt2.png"
            page.set_input_files('input[type="file"]', file_path)
            page.click('button:text("Process Receipt")')
            print("Uploaded a receipt for processing.")

            # Wait for the edit form to appear and be populated
            expect(page.locator("#edit-section")).to_be_visible(timeout=10000)
            expect(page.locator("#edit-vendor")).not_to_be_empty()
            print("Edit form is visible and populated.")

            # Modify a value in the form
            page.fill("#edit-vendor", "Test Vendor")
            page.click('button:text("Save Receipt")')
            print("Saved the edited receipt.")

            # Wait for the gallery to update with the new item
            expect(page.locator(".receipt-item", has_text="Test Vendor")).to_be_visible(timeout=10000)
            print("Receipt gallery updated with the new entry.")

            # Create verification directory if it doesn't exist
            os.makedirs("verification", exist_ok=True)

            screenshot_path = "verification/verification_final.png"
            page.screenshot(path=screenshot_path)
            print(f"Final verification screenshot saved to {screenshot_path}")

        except Exception as e:
            print(f"An error occurred: {e}")
            os.makedirs("verification", exist_ok=True)
            page.screenshot(path="verification/error_final.png")
        finally:
            browser.close()

if __name__ == "__main__":
    run()
