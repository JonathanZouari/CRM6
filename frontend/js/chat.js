/* Chat Page */

const messagesEl = document.getElementById("chat-messages");
const inputEl = document.getElementById("chat-input");

function sendSuggestion(chip) {
    inputEl.value = chip.textContent;
    sendMessage();
}

async function sendMessage() {
    const text = inputEl.value.trim();
    if (!text) return;

    inputEl.value = "";
    appendBubble("user", text);
    showTyping();

    try {
        const result = await api.post("/chat", { message: text });
        hideTyping();
        appendBubble("assistant", result.answer);
    } catch (err) {
        hideTyping();
        appendBubble("assistant", "Sorry, something went wrong. Please try again.");
    }
}

function appendBubble(role, text) {
    const bubble = document.createElement("div");
    bubble.className = `chat-bubble ${role}`;
    bubble.textContent = text;
    messagesEl.appendChild(bubble);
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function showTyping() {
    const el = document.createElement("div");
    el.className = "chat-bubble typing";
    el.id = "typing-indicator";
    el.textContent = "Thinking...";
    messagesEl.appendChild(el);
    messagesEl.scrollTop = messagesEl.scrollHeight;
}

function hideTyping() {
    const el = document.getElementById("typing-indicator");
    if (el) el.remove();
}
