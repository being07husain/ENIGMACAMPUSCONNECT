// session.js - Synchronizes user badge and handles logout across all CampusConnect views
(function () {
    const API_BASE = (window.location.protocol === 'file:' || (window.location.port !== '8000' && window.location.port !== ''))
        ? 'http://127.0.0.1:8000'
        : '';
    window.API_BASE = API_BASE;

    function getStoredUser() {
        try {
            return JSON.parse(localStorage.getItem("user") || "null");
        } catch (e) {
            return null;
        }
    }

    function syncUserBadges() {
        const user = getStoredUser();
        const displayName = user && user.fullname ? user.fullname : "Profile";

        // Update all .user-badge elements
        document.querySelectorAll(".user-badge").forEach(badge => {
            badge.style.cursor = "pointer";
            if (!badge.onclick && !badge.getAttribute("onclick")) {
                badge.onclick = () => window.location.href = "profile.html";
            }
            const span = badge.querySelector("span");
            if (span) {
                span.textContent = displayName;
            }
        });

        // Update any span immediately following profile.png (like in dashboard / clubs)
        document.querySelectorAll("img[src*='profile.png'] + span, span#dashboardUserName, span#topBarName").forEach(el => {
            if (el.id === "dashboardUserName") {
                el.textContent = displayName.toUpperCase();
            } else if (el.id === "topBarName") {
                el.textContent = displayName;
            } else {
                el.textContent = displayName.toUpperCase();
            }
        });

        // Setup logout links in sidebar
        document.querySelectorAll(".sidebar .navbar a, nav a").forEach(a => {
            if (a.textContent.trim().toLowerCase() === "logout") {
                a.href = "javascript:void(0)";
                a.onclick = function (e) {
                    e.preventDefault();
                    localStorage.removeItem("access_token");
                    localStorage.removeItem("user");
                    window.location.href = "login.html";
                };
            }
        });
    }

    // Run immediately and upon DOM readiness
    syncUserBadges();
    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", syncUserBadges);
    }

    // Fetch fresh user profile from API in background if logged in
    const token = localStorage.getItem("access_token");
    if (token) {
        fetch(API_BASE + "/api/auth/me", {
            headers: { "Authorization": `Bearer ${token}` }
        }).then(res => {
            if (res.status === 401) {
                localStorage.removeItem("access_token");
                localStorage.removeItem("user");
                window.location.href = "login.html";
                return null;
            }
            return res.ok ? res.json() : null;
        }).then(freshUser => {
            if (freshUser) {
                localStorage.setItem("user", JSON.stringify(freshUser));
                syncUserBadges();
            }
        }).catch(() => {});
    }
})();
