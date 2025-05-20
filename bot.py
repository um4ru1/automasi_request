from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import textwrap
import os
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage,
    BubbleContainer, BoxComponent, TextComponent, ButtonComponent
)
from linebot.models.actions import URIAction

app = Flask(__name__)

# Load environment variables
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

if not CHANNEL_ACCESS_TOKEN:
    raise ValueError("CHANNEL_ACCESS_TOKEN is not set. Check your environment variables.")
if not CHANNEL_SECRET:
    raise ValueError("CHANNEL_SECRET is not set. Check your environment variables.")

# Initialize LINE Bot API and Webhook Handler
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)
    print("Request body:", body)  # Debugging

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip().lower()

    if user_message == "melati2":
        reply_text = """GOOGLE CALENDAR:
https://tr.ee/KalenderRoseline

Form Pemesanan Jadwal Publikasi Grup Line:
https://tr.ee/FormPesanBcLINE

Form Penghapusan Jadwal Publikasi Grup Line:
https://tr.ee/FormHapusBcLINE
"""
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

    elif user_message == "rose1":
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="fdsafasdfa"))

    else:
        flex_message = FlexSendMessage(
            alt_text="Info Umum Atmosphaira",
            contents=BubbleContainer(
                body=BoxComponent(
                    layout="vertical",
                    contents=[
                        TextComponent(text="📚 ATMOSINFO", weight="bold", size="md"),
                        ButtonComponent(
                            style="link",
                            height="sm",
                            action=URIAction(
                                label="Lihat Dokumen",
                                uri="https://docs.google.com/document/d/1sISZQncRWjkxGBrkwovLo3i-mMC_EOp5BB2skRDVUlM/edit?tab=t.0"
                            )
                        ),
                        TextComponent(text="📁 ARSIPIN", weight="bold", size="md", margin="md"),
                        TextComponent(
                            text="Media Sosial HMME, Arsip, SOP, Form Pemesanan, Kalender",
                            size="sm", wrap=True
                        ),
                        ButtonComponent(
                            style="link",
                            height="sm",
                            action=URIAction(
                                label="Buka Arsipin",
                                uri="https://linktr.ee/ARSIPIN"
                            )
                        ),
                        TextComponent(text="🧭 Mengenal BP25", weight="bold", size="md", margin="md"),
                        ButtonComponent(
                            style="link",
                            height="sm",
                            action=URIAction(
                                label="Lihat Profil BP25",
                                uri="https://docs.google.com/document/d/1Q0vEWOAFjFtfU1hx-SiTuN1ttSCUn8MtC5IlZC53WuA/edit?tab=t.0"
                            )
                        ),
                        TextComponent(text="📅 Kalender Pusat", weight="bold", size="md", margin="md"),
                        ButtonComponent(
                            style="link",
                            height="sm",
                            action=URIAction(
                                label="Lihat Kalender BP25",
                                uri="https://calendar.google.com/calendar/embed?src=c_aee5d5c10e1ea4f22ce9252b92b378a948f2b43cd03000c3d3c7c1afe1d203ff%40group.calendar.google.com&ctz=Asia%2FJakarta"
                            )
                        ),
                    ]
                )
            )
        )

        line_bot_api.reply_message(event.reply_token, flex_message)
if __name__ == "__main__":
    app.run(port=8000)

@app.route("/notify", methods=["GET", "POST"])
def notify_admin():
    if request.method == "GET":
        return "Gunakan metode POST untuk mengirim notifikasi.", 405

    data = request.get_json()
    print("📥 Data POST diterima:", data)

    message_text = data.get("message", "📥 Ada request baru.")

    user_ids = [
        "U0e62a4a9406a1a35f4573665d5794bc7"
    ]

    try:
        line_bot_api.multicast(user_ids, TextSendMessage(text=message_text))
        print("✅ Berhasil kirim multicast!")
        return "✅ Notifikasi berhasil dikirim", 200
    except Exception as e:
        print(f"❌ Gagal kirim multicast: {str(e)}")
        return f"❌ Gagal kirim notifikasi: {str(e)}", 500



