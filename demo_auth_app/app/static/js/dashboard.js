document.addEventListener("DOMContentLoaded", async () => {
    const welcomeHeading = document.getElementById("welcome-heading");
    const profileUsername = document.getElementById("profile-username");
    const profileEmail = document.getElementById("profile-email");
    const profileId = document.getElementById("profile-id");
    const avatarInitial = document.getElementById("avatar-initial");
    const logoutBtn = document.getElementById("logout-btn");

    const token = sessionStorage.getItem("access_token");
    const headers = {};
    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    try {
        const response = await fetch("/api/me", {
            method: "GET",
            headers: headers,
            credentials: "include", // send cookies
        });

        if (!response.ok) {
            window.location.href = "/login";
            return;
        }

        const user = await response.json();
        if (welcomeHeading) welcomeHeading.textContent = `Welcome, ${user.username}!`;
        if (profileUsername) profileUsername.textContent = user.username;
        if (profileEmail) profileEmail.textContent = user.email;
        if (profileId) profileId.textContent = user.id;
        if (avatarInitial) avatarInitial.textContent = user.username.charAt(0).toUpperCase();
    } catch (err) {
        window.location.href = "/login";
    }

    if (logoutBtn) {
        logoutBtn.addEventListener("click", async () => {
            try {
                await fetch("/api/logout", {
                    method: "POST",
                    headers: headers,
                    credentials: "include",
                });
            } finally {
                sessionStorage.removeItem("access_token");
                window.location.href = "/login";
            }
        });
    }
});

