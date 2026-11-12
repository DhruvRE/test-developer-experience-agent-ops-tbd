"""UI tests for the Registration page using Playwright."""
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.ui
class TestUIRegistration:
    def test_registration_page_elements_present(self, page: Page, live_server_url: str):
        page.goto(f"{live_server_url}/register")
        expect(page).to_have_title("Register - Demo Auth App")
        expect(page.locator("h1")).to_have_text("Create Account")

        expect(page.locator("[data-testid='username-input']")).to_be_visible()
        expect(page.locator("[data-testid='email-input']")).to_be_visible()
        expect(page.locator("[data-testid='password-input']")).to_be_visible()
        expect(page.locator("[data-testid='confirm-password-input']")).to_be_visible()
        expect(page.locator("[data-testid='register-btn']")).to_be_visible()

    def test_registration_password_mismatch_validation(self, page: Page, live_server_url: str):
        page.goto(f"{live_server_url}/register")

        page.fill("[data-testid='username-input']", "ui_tester")
        page.fill("[data-testid='email-input']", "ui_tester@example.com")
        page.fill("[data-testid='password-input']", "Password123")
        page.fill("[data-testid='confirm-password-input']", "MismatchPassword456")
        page.click("[data-testid='register-btn']")

        error_alert = page.locator("[data-testid='error-alert']")
        expect(error_alert).to_be_visible()
        expect(error_alert).to_contain_text("Passwords do not match.")

    def test_successful_registration_and_redirect_to_login(self, page: Page, live_server_url: str):
        page.goto(f"{live_server_url}/register")

        page.fill("[data-testid='username-input']", "new_user")
        page.fill("[data-testid='email-input']", "new_user@example.com")
        page.fill("[data-testid='password-input']", "SecurePass123")
        page.fill("[data-testid='confirm-password-input']", "SecurePass123")
        page.click("[data-testid='register-btn']")

        success_alert = page.locator("[data-testid='success-alert']")
        expect(success_alert).to_be_visible()
        expect(success_alert).to_contain_text("Account created for new_user!")

        # Verify automatic redirect to /login
        page.wait_for_url(f"{live_server_url}/login", timeout=5000)
        expect(page).to_have_title("Login - Demo Auth App")

    def test_duplicate_registration_shows_server_error(self, page: Page, live_server_url: str):
        # First registration
        page.goto(f"{live_server_url}/register")
        page.fill("[data-testid='username-input']", "unique_user")
        page.fill("[data-testid='email-input']", "unique@example.com")
        page.fill("[data-testid='password-input']", "SecurePass123")
        page.fill("[data-testid='confirm-password-input']", "SecurePass123")
        page.click("[data-testid='register-btn']")
        page.wait_for_url(f"{live_server_url}/login")

        # Second registration attempt with identical username
        page.goto(f"{live_server_url}/register")
        page.fill("[data-testid='username-input']", "unique_user")
        page.fill("[data-testid='email-input']", "different_email@example.com")
        page.fill("[data-testid='password-input']", "SecurePass123")
        page.fill("[data-testid='confirm-password-input']", "SecurePass123")
        page.click("[data-testid='register-btn']")

        error_alert = page.locator("[data-testid='error-alert']")
        expect(error_alert).to_be_visible()
        expect(error_alert).to_contain_text("Username is already taken")

