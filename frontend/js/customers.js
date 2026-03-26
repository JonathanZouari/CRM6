/* Customers List Page */

let allCustomers = [];

document.addEventListener("DOMContentLoaded", () => {
    loadCustomers();
});

async function loadCustomers() {
    try {
        const statusFilter = document.getElementById("status-filter").value;
        const endpoint = statusFilter
            ? `/customers?status=${statusFilter}`
            : "/customers";
        allCustomers = await api.get(endpoint);
        updateStats();
        renderTable();
    } catch (err) {
        showError("Failed to load customers: " + err.message);
    }
}

function updateStats() {
    const total = allCustomers.length;
    const late = allCustomers.filter((c) => c.is_late).length;
    const inProgress = allCustomers.filter((c) => c.status === "in_progress").length;
    const closed = allCustomers.filter((c) => c.status === "closed").length;

    document.getElementById("stat-total").textContent = total;
    document.getElementById("stat-late").textContent = late;
    document.getElementById("stat-progress").textContent = inProgress;
    document.getElementById("stat-closed").textContent = closed;
}

function renderTable() {
    const searchTerm = document.getElementById("search-input").value.toLowerCase();
    const filtered = allCustomers.filter((c) =>
        c.name.toLowerCase().includes(searchTerm)
    );

    const tbody = document.getElementById("customers-table");
    const emptyState = document.getElementById("empty-state");

    if (filtered.length === 0) {
        tbody.innerHTML = "";
        emptyState.classList.remove("hidden");
        return;
    }

    emptyState.classList.add("hidden");
    tbody.innerHTML = filtered
        .map((c) => {
            const isLate = c.is_late;
            const rowClass = isLate ? "late-row clickable" : "clickable";
            const lateBadge = isLate ? '<span class="badge badge-late">LATE</span>' : "";
            const followUp = c.follow_up_at
                ? formatDate(c.follow_up_at) + lateBadge
                : "-";
            const lastContact = c.last_contact_at
                ? formatDate(c.last_contact_at)
                : "-";

            return `<tr class="${rowClass}" onclick="goToCustomer('${c.id}')">
                <td><strong>${escapeHtml(c.name)}</strong></td>
                <td>${escapeHtml(c.phone || "-")}</td>
                <td><span class="badge badge-${c.status}">${formatStatus(c.status)}</span></td>
                <td>${lastContact}</td>
                <td>${followUp}</td>
                <td class="actions" onclick="event.stopPropagation()">
                    <button class="btn btn-ghost btn-sm" onclick="openEditModal('${c.id}')" title="Edit">&#9998;</button>
                    <button class="btn btn-ghost btn-sm text-danger" onclick="deleteCustomer('${c.id}')" title="Delete">&#10005;</button>
                </td>
            </tr>`;
        })
        .join("");
}

function filterTable() {
    renderTable();
}

function goToCustomer(id) {
    window.location.href = `customer.html?id=${id}`;
}

function openAddModal() {
    document.getElementById("modal-title").textContent = "Add Customer";
    document.getElementById("edit-id").value = "";
    document.getElementById("form-name").value = "";
    document.getElementById("form-phone").value = "";
    document.getElementById("form-status").value = "new";
    document.getElementById("form-followup").value = "";
    document.getElementById("customer-modal").classList.add("active");
}

async function openEditModal(id) {
    try {
        const customer = await api.get(`/customers/${id}`);
        document.getElementById("modal-title").textContent = "Edit Customer";
        document.getElementById("edit-id").value = id;
        document.getElementById("form-name").value = customer.name;
        document.getElementById("form-phone").value = customer.phone || "";
        document.getElementById("form-status").value = customer.status;
        document.getElementById("form-followup").value = customer.follow_up_at
            ? toLocalDatetime(customer.follow_up_at)
            : "";
        document.getElementById("customer-modal").classList.add("active");
    } catch (err) {
        showError("Failed to load customer: " + err.message);
    }
}

function closeModal() {
    document.getElementById("customer-modal").classList.remove("active");
}

async function saveCustomer() {
    const id = document.getElementById("edit-id").value;
    const data = {
        name: document.getElementById("form-name").value.trim(),
        phone: document.getElementById("form-phone").value.trim(),
        status: document.getElementById("form-status").value,
        follow_up_at: document.getElementById("form-followup").value || null,
    };

    if (!data.name) {
        showError("Name is required");
        return;
    }

    try {
        if (id) {
            await api.put(`/customers/${id}`, data);
        } else {
            await api.post("/customers", data);
        }
        closeModal();
        await loadCustomers();
    } catch (err) {
        showError("Failed to save: " + err.message);
    }
}

async function deleteCustomer(id) {
    if (!confirm("Are you sure you want to delete this customer?")) return;
    try {
        await api.del(`/customers/${id}`);
        await loadCustomers();
    } catch (err) {
        showError("Failed to delete: " + err.message);
    }
}

/* Helpers */

function formatDate(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}

function toLocalDatetime(dateStr) {
    const d = new Date(dateStr);
    const offset = d.getTimezoneOffset();
    const local = new Date(d.getTime() - offset * 60 * 1000);
    return local.toISOString().slice(0, 16);
}

function formatStatus(status) {
    return status.replace("_", " ");
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

function showError(message) {
    alert(message);
}
