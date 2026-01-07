let currentChatId = null;

function createNewChat() {
    fetch("/new_chat", { method: "POST" })
        .then(res => res.json())
        .then(data => {
            currentChatId = data.chat_id;
            loadHistory();
            document.getElementById("chat-box").innerHTML = "";
        });
}

function loadHistory() {
    fetch("/history")
        .then(res => res.json())
        .then(chats => {
            let list = document.getElementById("chat-list");
            list.innerHTML = "";
            chats.forEach(chat => {
                let li = document.createElement("li");
                li.textContent = chat.title;
                li.onclick = () => loadMessages(chat.chat_id);
                list.appendChild(li);
            });
        });
}

function loadMessages(chatId) {
    currentChatId = chatId;

    fetch(`/messages/${chatId}`)
        .then(res => res.json())
        .then(msgs => {
            let chatBox = document.getElementById("chat-box");
            chatBox.innerHTML = "";

            msgs.forEach(m => {
                if (m.role === "system") return;

                let formattedContent = m.content
                    .split('\n')
                    .filter(line => line.trim() !== '')
                    .map(line => `<p>${line}</p>`)
                    .join('');

                chatBox.innerHTML += `
                    <div class="${m.role === "user" ? "user-message" : "assistant-message"}">
                        <b>${m.role === "user" ? "You" : "ChatGPT"}:</b>
                        ${formattedContent}
                    </div>
                    <div class="chat-divider"></div>
                `;
            });

            chatBox.scrollTop = chatBox.scrollHeight;
        });
}


function sendMessage() {
    let input = document.getElementById("user-input");
    let message = input.value.trim();
    if (!message || !currentChatId) return;

    input.value = "";

    fetch("/chat", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({ chat_id: currentChatId, message })
    })
    .then(res => res.json())
    .then(data => {
        loadMessages(currentChatId);
    });
}

createNewChat();
loadHistory();