/* Customer Detail Page */

let customerId = null;
let currentCustomer = null;

document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);
    customerId = params.get("id");
    if (!customerId) {
        window.location.href = "index.html";
        return;
    }
    loadAll();
});

async function loadAll() {
    await Promise.all([loadCustomer(), loadOrders(), loadTasks()]);
}

async function loadCustomer() {
    try {
        currentCustomer = await api.get(`/customers/${customerId}`);
        renderCustomerInfo(currentCustomer);
    } catch (err) {
        alert("Failed to load customer: " + err.message);
    }
}

function renderCustomerInfo(c) {
    document.getElementById("customer-name").textContent = c.name;
    document.title = `FlightCRM — ${c.name}`;
    document.getElementById("info-phone").textContent = c.phone || "-";
    document.getElementById("info-status").innerHTML =
        `<span class="badge badge-${c.status}">${c.status.replace("_", " ")}</span>` +
        (c.is_late ? ' <span class="badge badge-late">LATE</span>' : "");
    document.getElementById("info-created").textContent = c.created_at
        ? formatDate(c.created_at) : "-";
    document.getElementById("info-contact").textContent = c.last_contact_at
        ? formatDate(c.last_contact_at) : "-";
    document.getElementById("info-followup").textContent = c.follow_up_at
        ? formatDate(c.follow_up_at) : "-";
}

/* Orders */

async function loadOrders() {
    try {
        const orders = await api.get(`/customers/${customerId}/orders`);
        const tbody = document.getElementById("orders-table");
        const empty = document.getElementById("orders-empty");

        if (orders.length === 0) {
            tbody.innerHTML = "";
            empty.classList.remove("hidden");
            return;
        }
        empty.classList.add("hidden");
        tbody.innerHTML = orders
            .map(
                (o) => `<tr>
                <td><strong>${escapeHtml(o.destination)}</strong></td>
                <td>${o.departure_date}</td>
                <td>${o.return_date || "-"}</td>
                <td>$${Number(o.price).toLocaleString("en-US", { minimumFractionDigits: 2 })}</td>
                <td><span class="badge badge-${o.status}">${o.status}</span></td>
                <td class="actions">
                    <button class="btn btn-ghost btn-sm text-danger" onclick="deleteOrder('${o.id}')" title="Delete">&#10005;</button>
                </td>
            </tr>`
            )
            .join("");
    } catch (err) {
        alert("Failed to load orders: " + err.message);
    }
}

/* Tasks */

async function loadTasks() {
    try {
        const tasks = await api.get(`/customers/${customerId}/tasks`);
        const container = document.getElementById("tasks-list");
        const empty = document.getElementById("tasks-empty");

        const taskItems = tasks
            .map((t) => {
                const isDone = t.status === "done";
                const isOverdue = !isDone && new Date(t.due_date) < new Date();
                return `<div class="task-item">
                    <input type="checkbox" class="task-checkbox"
                        ${isDone ? "checked" : ""}
                        onchange="toggleTask('${t.id}', this.checked)">
                    <span class="task-title ${isDone ? 'done' : ''}">${escapeHtml(t.title)}</span>
                    <span class="task-due ${isOverdue ? 'overdue' : ''}">${t.due_date}</span>
                    <button class="btn btn-ghost btn-sm text-danger" onclick="deleteTask('${t.id}')" title="Delete">&#10005;</button>
                </div>`;
            })
            .join("");

        if (tasks.length === 0) {
            container.innerHTML = '<div class="empty-state" id="tasks-empty">No tasks yet.</div>';
        } else {
            container.innerHTML = taskItems;
        }
    } catch (err) {
        alert("Failed to load tasks: " + err.message);
    }
}

/* Edit Customer */

function openEditCustomer() {
    if (!currentCustomer) return;
    document.getElementById("edit-name").value = currentCustomer.name;
    document.getElementById("edit-phone").value = currentCustomer.phone || "";
    document.getElementById("edit-status").value = currentCustomer.status;
    document.getElementById("edit-followup").value = currentCustomer.follow_up_at
        ? toLocalDatetime(currentCustomer.follow_up_at)
        : "";
    document.getElementById("edit-modal").classList.add("active");
}

async function saveEditCustomer() {
    const data = {
        name: document.getElementById("edit-name").value.trim(),
        phone: document.getElementById("edit-phone").value.trim(),
        status: document.getElementById("edit-status").value,
        follow_up_at: document.getElementById("edit-followup").value || null,
    };
    if (!data.name) {
        alert("Name is required");
        return;
    }
    try {
        await api.put(`/customers/${customerId}`, data);
        closeAllModals();
        await loadCustomer();
    } catch (err) {
        alert("Failed to save: " + err.message);
    }
}

/* Order CRUD */

function openOrderModal() {
    document.getElementById("order-destination").value = "";
    document.getElementById("order-departure").value = "";
    document.getElementById("order-return").value = "";
    document.getElementById("order-price").value = "";
    document.getElementById("order-status").value = "offer";
    document.getElementById("order-modal").classList.add("active");
}

async function saveOrder() {
    const data = {
        destination: document.getElementById("order-destination").value.trim(),
        departure_date: document.getElementById("order-departure").value,
        return_date: document.getElementById("order-return").value || null,
        price: parseFloat(document.getElementById("order-price").value),
        status: document.getElementById("order-status").value,
    };
    if (!data.destination || !data.departure_date || isNaN(data.price)) {
        alert("Please fill in destination, departure date, and price");
        return;
    }
    try {
        await api.post(`/customers/${customerId}/orders`, data);
        closeAllModals();
        await loadOrders();
    } catch (err) {
        alert("Failed to save order: " + err.message);
    }
}

async function deleteOrder(orderId) {
    if (!confirm("Delete this order?")) return;
    try {
        await api.del(`/orders/${orderId}`);
        await loadOrders();
    } catch (err) {
        alert("Failed to delete order: " + err.message);
    }
}

/* Task CRUD */

function openTaskModal() {
    document.getElementById("task-title").value = "";
    document.getElementById("task-due").value = "";
    document.getElementById("task-modal").classList.add("active");
}

async function saveTask() {
    const data = {
        title: document.getElementById("task-title").value.trim(),
        due_date: document.getElementById("task-due").value,
    };
    if (!data.title || !data.due_date) {
        alert("Please fill in title and due date");
        return;
    }
    try {
        await api.post(`/customers/${customerId}/tasks`, data);
        closeAllModals();
        await loadTasks();
    } catch (err) {
        alert("Failed to save task: " + err.message);
    }
}

async function toggleTask(taskId, isDone) {
    try {
        await api.put(`/tasks/${taskId}`, { status: isDone ? "done" : "open" });
        await loadTasks();
    } catch (err) {
        alert("Failed to update task: " + err.message);
    }
}

async function deleteTask(taskId) {
    if (!confirm("Delete this task?")) return;
    try {
        await api.del(`/tasks/${taskId}`);
        await loadTasks();
    } catch (err) {
        alert("Failed to delete task: " + err.message);
    }
}

/* Modal helpers */

function closeAllModals() {
    document.querySelectorAll(".modal-overlay").forEach((m) =>
        m.classList.remove("active")
    );
}

/* Shared helpers */

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

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}
