/** Shared nav, theme toggle, mobile sidebar */
(function () {
  const THEME_KEY = "studyhub_theme";

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem(THEME_KEY, theme);
    const btn = document.getElementById("theme-toggle");
    if (btn) btn.textContent = theme === "light" ? "Dark mode" : "Light mode";
  }

  function initTheme() {
    const saved = localStorage.getItem(THEME_KEY) || "dark";
    applyTheme(saved);
    document.getElementById("theme-toggle")?.addEventListener("click", () => {
      const next = document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light";
      applyTheme(next);
    });
  }

  function initMobileNav() {
    const sidebar = document.querySelector(".sidebar");
    const toggle = document.getElementById("nav-toggle");
    const overlay = document.getElementById("nav-overlay");
    if (!sidebar || !toggle) return;
    toggle.addEventListener("click", () => {
      sidebar.classList.toggle("open");
      overlay?.classList.toggle("open");
    });
    overlay?.addEventListener("click", () => {
      sidebar.classList.remove("open");
      overlay.classList.remove("open");
    });
    sidebar.querySelectorAll("nav a").forEach((a) => {
      a.addEventListener("click", () => {
        sidebar.classList.remove("open");
        overlay?.classList.remove("open");
      });
    });
  }

  window.initLayout = function (active) {
    const nav = document.querySelector(".sidebar nav");
    if (nav && !nav.querySelector('[data-layout="calendar"]')) {
      const extra = `
        <a href="/calendar.html" data-layout="calendar">Calendar</a>
        <a href="/profile.html" data-layout="profile">Profile</a>`;
      nav.insertAdjacentHTML("beforeend", extra);
    }
    nav?.querySelectorAll("a").forEach((a) => {
      a.classList.toggle("active", a.getAttribute("href")?.includes(active));
    });
    initTheme();
    initMobileNav();
  };
})();
