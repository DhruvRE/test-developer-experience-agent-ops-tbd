"""UI tests for Dashboard and logout flow using Playwright."""
import pytest
from playwright.sync_api import Page, expect

@pytest.mark.ui
class TestUIDashboard:
    def test_unauthenticated_dashboard_redirects_to_login(self, page: Page, live_server_url: str):
        page.goto(f"{live_server_url}/dashboard")
        page.wait_for_url(f"{live_server_url}/login", timeout=5000)
        expect(page).to_have_title("Login - Demo Auth App")

    def test_dashboard_shows_profile_and_logout_flow(self, page: Page, live_server_url: str):
        # 1. Register
        page.goto(f"{live_server_url}/register")
        page.fill("[data-testid='username-input']", "dashboard_user")
        page.fill("[data-testid='email-input']", "dashboard_user@example.com")
        page.fill("[data-testid='password-input']", "SecurePass123")
        page.fill("[data-testid='confirm-password-input']", "SecurePass123")
        page.click("[data-testid='register-btn']")
        page.wait_for_url(f"{live_server_url}/login")

        # 2. Login
        page.fill("[data-testid='username-input']", "dashboard_user")
        page.fill("[data-testid='password-input']", "SecurePass123")
        page.click("[data-testid='login-btn']")
        page.wait_for_url(f"{live_server_url}/dashboard")

        # 3. Verify Profile details displayed
        expect(page.locator("[data-testid='profile-username']")).to_have_text("dashboard_user")
        expect(page.locator("[data-testid='profile-email']")).to_have_text("dashboard_user@example.com")
        expect(page.locator("[data-testid='profile-id']")).not_to_have_text("--")

        # 4. Click Log Out button
        page.click("[data-testid='logout-btn']")

        # 5. Verify redirection to /login
        page.wait_for_url(f"{live_server_url}/login", timeout=5000)
        expect(page).to_have_title("Login - Demo Auth App")

