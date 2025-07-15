document.addEventListener("DOMContentLoaded", () => {
    const chatContainer = document.getElementById("chat-container");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const clearBtn = document.getElementById("clear-btn");
    const loading = document.getElementById("loading");
    const suggestions = document.getElementById("suggestions");

    // Initialize toastr
    toastr.options = {
        positionClass: "toast-top-right",
        timeOut: 3000,
        progressBar: true
    };

    // Show welcome modal
    const welcomeModal = new bootstrap.Modal(document.getElementById("welcomeModal"));
    welcomeModal.show();

    // Initialize particles.js
    particlesJS("particles-js", {
        particles: {
            number: { value: 80, density: { enable: true, value_area: 800 } },
            color: { value: "#ffffff" },
            shape: { type: "circle" },
            opacity: { value: 0.5, random: true },
            size: { value: 3, random: true },
            line_linked: { enable: false },
            move: { enable: true, speed: 2, direction: "none", random: true }
        },
        interactivity: {
            events: { onhover: { enable: true, mode: "repulse" }, onclick: { enable: true, mode: "push" } },
            modes: { repulse: { distance: 100 }, push: { particles_nb: 4 } }
        }
    });

    // Send query on button click
    sendBtn.addEventListener("click", sendMessage);
    // Send query on Enter key
    userInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });

    // Clear chat history
    clearBtn.addEventListener("click", async () => {
        try {
            const response = await fetch("/api/clear", { method: "POST" });
            const data = await response.json();
            if (data.status === "success") {
                chatContainer.innerHTML = '<div class="message bot-message" data-timestamp="2025-07-15 20:00">Welcome to the MOSDAC Chatbot! Ask about satellites, meteorology, or oceanography to explore our scientific database.</div>';
                suggestions.innerHTML = "";
                toastr.success(data.response);
            } else {
                toastr.error(data.response);
            }
        } catch (error) {
            toastr.error(`Error: ${error.message}`);
        }
    });

    async function sendMessage(query = userInput.value.trim()) {
        if (!query) {
            toastr.warning("Please enter a question.");
            return;
        }

        // Add user message
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
                displaySuggestions(data.suggestions);
                toastr.success("Response received!");
            } else {
                appendMessage(`Error: ${data.response}`, "bot-message text-danger");
                toastr.error(data.response);
            }
        } catch (error) {
            loading.classList.add("d-none");
            appendMessage(`Error: ${error.message}`, "bot-message text-danger");
            toastr.error(`Error: ${error.message}`);
        }

        // Scroll to bottom
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function appendMessage(text, className) {
        const messageDiv = document.createElement("div");
        messageDiv.className = `message ${className}`;
        messageDiv.textContent = text;
        const timestamp = new Date().toLocaleTimeString();
        messageDiv.dataset.timestamp = timestamp;
        messageDiv.innerHTML += `<span class="timestamp">${timestamp}</span>`;
        chatContainer.appendChild(messageDiv);
    }

    function displaySuggestions(suggestionList) {
        suggestions.innerHTML = "";
        if (suggestionList.length > 0) {
            const suggestionDiv = document.createElement("div");
            suggestionDiv.innerHTML = "<strong>Suggested Questions:</strong>";
            suggestionList.forEach(suggestion => {
                const btn = document.createElement("button");
                btn.className = "btn btn-sm btn-outline-light";
                btn.textContent = suggestion;
                btn.addEventListener("click", () => sendMessage(suggestion));
                suggestionDiv.appendChild(btn);
            });
            suggestions.appendChild(suggestionDiv);
        }
    }
});