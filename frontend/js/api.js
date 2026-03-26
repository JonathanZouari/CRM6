/* API Client — Flight Tickets CRM */

const API_BASE = window.API_BASE_URL || "http://localhost:5000";

async function apiFetch(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
        headers: { "Content-Type": "application/json" },
        ...options,
    };
    if (config.body && typeof config.body === "object") {
        config.body = JSON.stringify(config.body);
    }
    const response = await fetch(url, config);
    const data = await response.json();
    if (!data.success) {
        throw new Error(data.error || "Request failed");
    }
    return data.data;
}

const api = {
    get: (path) => apiFetch(path),
    post: (path, body) => apiFetch(path, { method: "POST", body }),
    put: (path, body) => apiFetch(path, { method: "PUT", body }),
    del: (path) => apiFetch(path, { method: "DELETE" }),
};
