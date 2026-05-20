const API_BASE = "";

function getToken() {
  return localStorage.getItem("studyhub_token");
}

function setToken(token) {
  if (token) localStorage.setItem("studyhub_token", token);
  else localStorage.removeItem("studyhub_token");
}

async function api(path, options = {}) {
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (res.status === 401) {
    setToken(null);
    if (!window.location.pathname.endsWith("/login.html")) {
      window.location.href = "/login.html?session=expired";
    }
    throw new Error("Unauthorized");
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(formatApiError(err) || res.statusText || "Request failed");
  }
  if (res.status === 204) return null;
  return res.json();
}

function requireAuth() {
  if (!getToken()) {
    window.location.href = "/login.html";
    return false;
  }
  return true;
}

function formatApiError(err) {
  const detail = err?.detail;
  if (Array.isArray(detail)) {
    return detail.map((d) => d.msg || JSON.stringify(d)).join("; ");
  }
  if (typeof detail === "string") return detail;
  return null;
}

function showError(el, message) {
  if (!el) return;
  el.textContent = message;
  el.classList.remove("hidden");
}

function formatMinutes(m) {
  const h = Math.floor(m / 60);
  const min = m % 60;
  if (h === 0) return `${min}m`;
  return min ? `${h}h ${min}m` : `${h}h`;
}

function escapeHtml(text) {
  if (text == null) return "";
  const div = document.createElement("div");
  div.textContent = String(text);
  return div.innerHTML;
}

function courseUrl(id) {
  return `/course.html?id=${id}`;
}

async function downloadCsv(path, filename) {
  const token = getToken();
  const res = await fetch(`${API_BASE}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (res.status === 401) {
    setToken(null);
    window.location.href = "/login.html?session=expired";
    return;
  }
  if (!res.ok) throw new Error("Export failed");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function formatDate(iso) {
  if (!iso) return "—";
  return new Date(iso + "T00:00:00").toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}
