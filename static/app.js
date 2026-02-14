const messagesContainer = document.getElementById("messages");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

const messages = [];

chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const text = userInput.value.trim();
    if (!text) return;

    messages.push({ role: "user", content: text });
    renderMessage("user", text);

    userInput.value = "";
    userInput.style.height = "auto";
    sendBtn.disabled = true;

    sendMessage();
});

userInput.addEventListener("input", () => {
    userInput.style.height = "auto";
    userInput.style.height = userInput.scrollHeight + "px";
});

userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        chatForm.requestSubmit();
    }
});

function renderMessage(role, content) {
    const div = document.createElement("div");
    div.className = `message ${role}`;
    div.textContent = content;
    messagesContainer.appendChild(div);
    scrollToBottom();
    return div;
}

function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

async function sendMessage() {
    const bubble = renderMessage("assistant", "");

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ messages }),
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";
        let fullText = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const parts = buffer.split("\n\n");
            buffer = parts.pop();

            for (const part of parts) {
                const line = part.trim();
                if (!line.startsWith("data: ")) continue;

                const data = line.slice(6);
                if (data === "[DONE]") continue;

                const parsed = JSON.parse(data);
                if (parsed.error) {
                    throw new Error(parsed.error);
                }
                fullText += parsed.content;
                bubble.textContent = fullText;
                scrollToBottom();
            }
        }

        messages.push({ role: "assistant", content: fullText });
    } catch (err) {
        if (!bubble.textContent) {
            bubble.remove();
        }
        const errorDiv = document.createElement("div");
        errorDiv.className = "message error";
        errorDiv.textContent = `Error: ${err.message}`;
        messagesContainer.appendChild(errorDiv);
        scrollToBottom();
    } finally {
        sendBtn.disabled = false;
        userInput.focus();
    }
}
