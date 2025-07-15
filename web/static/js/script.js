document.addEventListener("DOMContentLoaded", () => {
    const chatContainer = document.getElementById("chat-container");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const loading = document.getElementById("loading");

    // Send query on button click
    sendBtn.addEventListener("click", sendMessage);
    // Send query on Enter key
    userInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });

    async function sendMessage() {
        const query = userInput.value.trim();
        if (!query) return;

        // Add user message to chat
        appendMessage(query, "user-message");
        userInput.value = "";
        loading.classList.remove("d-none");

        try {
            const response = await fetch("/api/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query })
            });
            const data = await response.json();
            loading.classList.add("d-none");

            if (data.status === "success") {
                appendMessage(data.response, "bot-message");
            } else {
                appendMessage(`Error: ${data.response}`, "bot-message text-danger");
            }
        } catch (error) {
            loading.classList.add("d-none");
            appendMessage(`Error: ${error.message}`, "bot-message text-danger");
        }

        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function appendMessage(text, className) {
        const messageDiv = document.createElement("div");
        messageDiv.className = `message ${className}`;
        messageDiv.textContent = text;
        chatContainer.appendChild(messageDiv);
    }
});