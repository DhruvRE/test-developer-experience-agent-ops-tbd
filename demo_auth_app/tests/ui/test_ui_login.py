"""UI tests for the Login page using Playwright."""
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.ui
class TestUILogin:
    def test_login_page_renders_properly(self, page: Page, live_server_url: str):
        page.goto(f"{live_server_url}/login")
        expect(page).to_have_title("Login - Demo Auth App")
        expect(page.locator("[data-testid='username-input']")).to_be_visible()
        expect(page.locator("[data-testid='password-input']")).to_be_visible()
        expect(page.locator("[data-testid='login-btn']")).to_be_visible()

    def test_navigation_from_login_to_register(self, page: Page, live_server_url: str):
        page.goto(f"{live_server_url}/login")
        page.click("[data-testid='register-link']")
        page.wait_for_url(f"{live_server_url}/register")
        expect(page).to_have_title("Register - Demo Auth App")

    def test_login_with_invalid_credentials_shows_alert(self, page: Page, live_server_url: str):
        page.goto(f"{live_server_url}/login")
        page.fill("[data-testid='username-input']", "non_existing_user")
        page.fill("[data-testid='password-input']", "WrongPassword123")
        page.click("[data-testid='login-btn']")

        error_alert = page.locator("[data-testid='error-alert']")
        expect(error_alert).to_be_visible()
        expect(error_alert).to_contain_text("Invalid username or password.")

    def test_login_successful_redirects_to_dashboard(self, page: Page, live_server_url: str):
        # 1. Register user
        page.goto(f"{live_server_url}/register")
        page.fill("[data-testid='username-input']", "valid_login_user")
        page.fill("[data-testid='email-input']", "valid_login@example.com")
        page.fill("[data-testid='password-input']", "MySecurePass1")
        page.fill("[data-testid='confirm-password-input']", "MySecurePass1")
        page.click("[data-testid='register-btn']")
        page.wait_for_url(f"{live_server_url}/login")

        # 2. Login
        page.fill("[data-testid='username-input']", "valid_login_user")
        page.fill("[data-testid='password-input']", "MySecurePass1")
        page.click("[data-testid='login-btn']")

        # 3. Assert redirected to dashboard
        page.wait_for_url(f"{live_server_url}/dashboard", timeout=5000)
        expect(page).to_have_title("Dashboard - Demo Auth App")
        expect(page.locator("[data-testid='welcome-heading']")).to_contain_text("Welcome, valid_login_user!")

