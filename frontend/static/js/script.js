document.addEventListener("DOMContentLoaded", () => {
    const chatContainer = document.getElementById("chat-container");
    const userInput = document.getElementById("user-input");
    const sendBtn = document.getElementById("send-btn");
    const clearBtn = document.getElementById("clear-btn");
    const exportBtn = document.getElementById("export-btn");
    const loading = document.getElementById("loading");
    const suggestions = document.getElementById("suggestions");
    const sidebar = document.getElementById("sidebar");
    const sidebarToggle = document.getElementById("sidebar-toggle");
    const themeToggle = document.getElementById("theme-toggle");
    const loadingScreen = document.getElementById("loading-screen");
    const searchInput = document.getElementById("search-input");
    const feedbackForm = document.getElementById("feedback-form");
    const progressBar = document.getElementById("progress-bar");

    // Initialize toastr
    toastr.options = {
        positionClass: "toast-top-right",
        timeOut: 3000,
        progressBar: true
    };

    // Hide loading screen
    setTimeout(() => {
        loadingScreen.style.display = "none";
    }, 2000);

    // Show welcome modal
    const welcomeModal = new bootstrap.Modal(document.getElementById("welcomeModal"));
    welcomeModal.show();

    // Initialize particles.js
    particlesJS("particles-js", {
        particles: {
            number: { value: 100, density: { enable: true, value_area: 800 } },
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

    // Sidebar toggle
    sidebarToggle.addEventListener("click", () => {
        sidebar.classList.toggle("active");
    });

    // Theme toggle
    themeToggle.addEventListener("click", () => {
        document.body.classList.toggle("light-mode");
        themeToggle.textContent = document.body.classList.contains("light-mode")
            ? "Switch to Dark Mode"
            : "Switch to Light Mode";
    });

    // Search autocomplete
    const staticSuggestions = [
        "INSAT-3D", "Weather data", "Oceanographic satellites", "MOSDAC mission",
        "Satellite imagery", "Meteorological data", "Cyclone tracking"
    ];
    let searchSuggestions = staticSuggestions;

    // Dynamic suggestions from API
    async function fetchSuggestions(query) {
        try {
            const response = await fetch("/api/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query })
            });
            const data = await response.json();
            return data.suggestions || staticSuggestions;
        } catch (error) {
            console.error("Error fetching suggestions:", error);
            return staticSuggestions;
        }
    }

    // Initialize autocomplete with error handling
    try {
        if (typeof $.ui === "undefined") {
            throw new Error("jQuery UI not loaded");
        }
        $("#search-input").autocomplete({
            source: async (request, response) => {
                searchSuggestions = await fetchSuggestions(request.term);
                response(searchSuggestions);
            },
            appendTo: "#search-suggestions",
            select: (event, ui) => {
                sendMessage(ui.item.value);
                searchInput.value = "";
                return false;
            },
            minLength: 2
        });
    } catch (error) {
        console.error("Autocomplete initialization failed:", error);
        toastr.error("Search functionality unavailable. Using static suggestions.");
        $("#search-input").on("input", () => {
            const value = searchInput.value.toLowerCase();
            const filtered = staticSuggestions.filter(s => s.toLowerCase().includes(value));
            const suggestionDiv = document.getElementById("search-suggestions");
            suggestionDiv.innerHTML = filtered.map(s => `<div class="ui-menu-item">${s}</div>`).join("");
            suggestionDiv.querySelectorAll(".ui-menu-item").forEach(item => {
                item.addEventListener("click", () => {
                    sendMessage(item.textContent);
                    searchInput.value = "";
                    suggestionDiv.innerHTML = "";
                });
            });
        });
    }

    // Send query
    sendBtn.addEventListener("click", sendMessage);
    userInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendMessage();
    });

    // Clear chat
    clearBtn.addEventListener("click", async () => {
        try {
            const response = await fetch("/api/clear", { method: "POST" });
            const data = await response.json();
            if (data.status === "success") {
                chatContainer.innerHTML = '<div class="message bot-message" data-timestamp="2025-07-15 20:00">Welcome to the MOSDAC Chatbot! Explore our scientific database by asking about satellites, meteorology, or oceanography.</div>';
                suggestions.innerHTML = "";
                toastr.success(data.response);
            } else {
                toastr.error(data.response);
            }
        } catch (error) {
            toastr.error(`Error: ${error.message}`);
        }
    });

    // Export chat history
    exportBtn.addEventListener("click", () => {
        const messages = Array.from(chatContainer.querySelectorAll(".message")).map(m => {
            const isUser = m.classList.contains("user-message");
            return `[${m.dataset.timestamp}] ${isUser ? "User" : "Bot"}: ${m.textContent.replace(m.querySelector(".timestamp").textContent, "").trim()}`;
        }).join("\n");
        const blob = new Blob([messages], { type: "text/plain" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "mosdac_chat_history.txt";
        a.click();
        URL.revokeObjectURL(url);
        toastr.success("Chat history exported!");
    });

    // Feedback form
    feedbackForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const feedback = document.getElementById("feedback-text").value.trim();
        if (!feedback) {
            toastr.warning("Please enter feedback.");
            return;
        }
        try {
            const response = await fetch("/api/feedback", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ feedback })
            });
            const data = await response.json();
            if (data.status === "success") {
                toastr.success(data.response);
                document.getElementById("feedback-text").value = "";
                bootstrap.Modal.getInstance(document.getElementById("feedbackModal")).hide();
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

        // Animate progress bar
        let progress = 0;
        const progressInterval = setInterval(() => {
            progress += 10;
            progressBar.style.width = `${progress}%`;
            if (progress >= 100) clearInterval(progressInterval);
        }, 200);

        try {
            const response = await fetch("/api/ask", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query })
            });
            const data = await response.json();
            clearInterval(progressInterval);
            progressBar.style.width = "0%";
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
            clearInterval(progressInterval);
            progressBar.style.width = "0%";
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

    window.showModal = function() {
        welcomeModal.show();
    };

    window.showFeedbackModal = function() {
        const feedbackModal = new bootstrap.Modal(document.getElementById("feedbackModal"));
        feedbackModal.show();
    };
});