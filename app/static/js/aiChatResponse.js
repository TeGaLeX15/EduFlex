const chatMessages = document.getElementById("chat-messages");
let allMessages = []; // Храним все сообщения

// Открыть окно чата и очистить старые сообщения
function openChat() {
    allMessages = [];
    updateChat([]);
    document.getElementById("chat-modal").classList.add("active");
    document.getElementById("user-question").focus();
}

// Закрыть окно чата
function closeChat() {
    document.getElementById("chat-modal").classList.remove("active");
}

// Обновление чата
function updateChat(messages) {
    chatMessages.innerHTML = '';

    if (messages.length === 0) {
        chatMessages.classList.add('empty');
        chatMessages.innerHTML = `
            <div class="empty-message">
                🤖 Я — ваш помощник. Задайте вопрос по уроку, и я постараюсь помочь!
            </div>
        `;
    } else {
        chatMessages.classList.remove('empty');
        messages.forEach(({ text, from }) => {
            const div = document.createElement('div');
            div.className = 'message ' + (from === 'user' ? 'user' : 'bot');
            div.innerHTML = text;
            chatMessages.appendChild(div);
        });
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Добавление сообщения
function addMessage(text, from = 'user') {
    const formattedText = from === 'bot' ? formatAIResponse(text) : escapeHtml(text);
    allMessages.push({ text: formattedText, from });
    updateChat(allMessages);
}

// Экранирование HTML для безопасности
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Форматирование ответа ИИ
function formatAIResponse(rawText) {
    const escapeHtml = (text) => {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    };

    let formatted = '';
    let inCodeBlock = false;
    const lines = rawText.split('\n');

    for (let line of lines) {
        if (line.trim().startsWith("```")) {
            formatted += inCodeBlock ? "</code></pre>" : "<pre><code>";
            inCodeBlock = !inCodeBlock;
            continue;
        }

        if (inCodeBlock) {
            formatted += escapeHtml(line) + "\n";
            continue;
        }

        const inlineCodePattern = /`([^`]+)`/g;
        const processedLine = line.replace(inlineCodePattern, (_, code) => `<code>${escapeHtml(code)}</code>`);
        formatted += processedLine + "<br>";
    }

    if (inCodeBlock) {
        formatted += "</code></pre>";
    }

    return formatted;
}

// Отправка вопроса
async function sendQuestion() {
    const input = document.getElementById("user-question");
    const message = input.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    input.value = "";

    // Получаем контекст урока
    const context = document.getElementById("lesson-context").textContent || "";

    // Добавляем пустое сообщение ИИ, чтобы потом заполнять
    const botPlaceholder = { text: '', from: 'bot' };
    allMessages.push(botPlaceholder);
    updateChat(allMessages);

    try {
        const response = await fetch("/chat-stream", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message, context })
        });

        if (!response.ok || !response.body) {
            botPlaceholder.text = "Ошибка ответа от ИИ.";
            updateChat(allMessages);
            return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });

            const parts = buffer.split("\n\n");
            buffer = parts.pop();

            for (let part of parts) {
                if (part.startsWith("data:")) {
                    const text = part.replace(/^data:\s*/, "");
                    botPlaceholder.text += formatAIResponse(text);
                    updateChat(allMessages);
                }
            }
        }
    } catch (err) {
        botPlaceholder.text = "Сбой соединения с сервером.";
        updateChat(allMessages);
    }
}

// Отправка по Enter
document.getElementById("user-question").addEventListener("keydown", function(e) {
    if (e.key === "Enter") {
        e.preventDefault();
        sendQuestion();
    }
});
