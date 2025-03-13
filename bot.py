import os
from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError

# **🔹 Ambil Token & Secret dari Environment (Koyeb)**
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

# **🔹 Inisialisasi Flask & LINE Bot API**
app = Flask(__name__)
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature", 400

    return "OK", 200


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # **🔹 Jika bot berada di grup, ambil Group ID**
    if event.source.type == "group":
        group_id = event.source.group_id
        reply_text = f"Group ID: {group_id}"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        print(f"✅ Group ID: {group_id}")  # Log di terminal

    else:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Silakan gunakan bot ini di dalam grup!"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
