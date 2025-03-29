from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

if not CHANNEL_ACCESS_TOKEN:
    raise ValueError("CHANNEL_ACCESS_TOKEN is not set. Check your environment variables.")
if not CHANNEL_SECRET:
    raise ValueError("CHANNEL_SECRET is not set. Check your environment variables.")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    body = request.get_data(as_text=True)
    print("Request body:", body)  # Debugging
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    help_message = (
        "Berikut beberapa pilihan:
"
        "bru1 = hj -> Berikut link kalender, broadcast, dsb.
"
        "bru2 = hi -> Berikut link pengajuan agenda.
"
        "bru3 = hy -> Berikut link pengajuan ...
"
        "bru4 = he -> Berikut link pengajuan ..."
    )
    
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=help_message))

if __name__ == "__main__":
    app.run(port=8000)
