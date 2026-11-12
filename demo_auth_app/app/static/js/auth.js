document.addEventListener("DOMContentLoaded", () => {
    const registerForm = document.getElementById("register-form");
    const loginForm = document.getElementById("login-form");
    const errorAlert = document.getElementById("error-alert");
    const successAlert = document.getElementById("success-alert");

    function showError(message) {
        if (errorAlert) {
            errorAlert.textContent = message;
            errorAlert.style.display = "block";
        }
        if (successAlert) {
            successAlert.style.display = "none";
        }
    }

    function showSuccess(message) {
        if (successAlert) {
            successAlert.textContent = message;
            successAlert.style.display = "block";
        }
        if (errorAlert) {
            errorAlert.style.display = "none";
        }
    }

    // Handle Register Form
    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const username = document.getElementById("username").value.trim();
            const email = document.getElementById("email").value.trim();
            const password = document.getElementById("password").value;
            const confirm_password = document.getElementById("confirm_password").value;

            // Client-side quick checks
            if (password !== confirm_password) {
                showError("Passwords do not match.");
                return;
            }

            try {
                const response = await fetch("/api/register", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, email, password, confirm_password }),
                });

                const data = await response.json();
                if (!response.ok) {
                    showError(data.detail || "Registration failed. Please check your inputs.");
                } else {
                    showSuccess(`Account created for ${data.username}! Redirecting to login...`);
                    registerForm.reset();
                    setTimeout(() => {
                        window.location.href = "/login";
                    }, 1200);
                }
            } catch (err) {
                showError("Network error. Please try again.");
            }
        });
    }

    // Handle Login Form
    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const username = document.getElementById("username").value.trim();
            const password = document.getElementById("password").value;

            try {
                const response = await fetch("/api/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username, password }),
                });

                const data = await response.json();
                if (!response.ok) {
                    showError(data.detail || "Invalid credentials.");
                } else {
                    showSuccess("Login successful! Redirecting...");
                    if (data.access_token) {
                        sessionStorage.setItem("access_token", data.access_token);
                    }
                    setTimeout(() => {
                        window.location.href = "/dashboard";
                    }, 800);
                }
            } catch (err) {
                showError("Network error. Please try again.");
            }
        });
    }
});

