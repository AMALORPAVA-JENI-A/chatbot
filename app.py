import os
import uuid
from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
print(os.getenv("GROQ_API_KEY"))
# Store all conversations
conversations = {}

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are ChatGPT, a helpful, clear, and polite AI assistant. "
        "Explain things step by step and give examples when needed."
    )
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/new_chat", methods=["POST"])
def new_chat():
    chat_id = str(uuid.uuid4())
    conversations[chat_id] = [SYSTEM_PROMPT]
    return jsonify({"chat_id": chat_id})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    chat_id = data.get("chat_id")
    user_message = data.get("message")

    if chat_id not in conversations:
        return jsonify({"error": "Invalid chat ID"}), 400

    conversations[chat_id].append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=conversations[chat_id],
            temperature=0.7
        )

        bot_reply = response.choices[0].message.content
        conversations[chat_id].append(
            {"role": "assistant", "content": bot_reply}
        )

        return jsonify({"reply": bot_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/history", methods=["GET"])
def history():
    history_list = []

    for cid, conv in conversations.items():
        # Check if any user message exists
        user_messages = [m for m in conv if m["role"] == "user"]

        if user_messages:
            history_list.append({
                "chat_id": cid,
                "title": user_messages[0]["content"][:30]
            })

    return jsonify(history_list)


@app.route("/messages/<chat_id>")
def messages(chat_id):
    return jsonify(conversations.get(chat_id, []))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860)
