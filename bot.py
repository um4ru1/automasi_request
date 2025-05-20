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

from linebot.models import (
    FlexSendMessage, BubbleContainer, ImageComponent, BoxComponent,
    TextComponent, ButtonComponent, URIAction
)

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
                hero=ImageComponent(
                    url="https://i.imgur.com/kUiLxRD.png",
                    size="full",
                    aspect_ratio="20:13",
                    aspect_mode="cover"
                ),
                body=BoxComponent(
                    layout="vertical",
                    spacing="md",
                    contents=[
                        BoxComponent(
                            layout="vertical",
                            background_color="#DBEAFE",
                            corner_radius="md",
                            padding_all="12px",
                            contents=[
                                TextComponent(
                                    text="ATMOSINFO",
                                    weight="bold",
                                    size="lg",
                                    align="center",
                                    color="#000000"
                                )
                            ]
                        ),
                        BoxComponent(
                            layout="vertical",
                            background_color="#DBEAFE",
                            corner_radius="md",
                            padding_all="12px",
                            spacing="sm",
                            contents=[
                                TextComponent(
                                    text="ARSIPIN",
                                    weight="bold",
                                    size="md",
                                    color="#000000"
                                ),
                                TextComponent(
                                    text="Link pusat yang berisi Media Sosial HMME, Arsip pusat, SOP, Form Pemesanan, dan Kalender",
                                    size="xs",
                                    wrap=True
                                ),
                                ButtonComponent(
                                    style="primary",
                                    height="sm",
                                    color="#1C398E",
                                    action=URIAction(
                                        label="Buka Arsipin",
                                        uri="https://linktr.ee/ARSIPIN"
                                    ),
                                    margin="md"
                                )
                            ]
                        ),
                        BoxComponent(
                            layout="vertical",
                            background_color="#DBEAFE",
                            corner_radius="md",
                            padding_all="12px",
                            spacing="sm",
                            contents=[
                                TextComponent(
                                    text="MENGENAL BP25",
                                    weight="bold",
                                    size="md",
                                    color="#000000"
                                ),
                                TextComponent(
                                    text="Cek Deskripsi Badan Pengurus HMME 'Atmosphaira' ITB 2025",
                                    size="xs",
                                    wrap=True
                                ),
                                ButtonComponent(
                                    style="primary",
                                    height="sm",
                                    color="#1C398E",
                                    action=URIAction(
                                        label="Lihat Profil BP25",
                                        uri="https://docs.google.com/document/d/1Q0vEWOAFjFtfU1hx-SiTuN1ttSCUn8MtC5IlZC53WuA/edit?tab=t.0"
                                    ),
                                    margin="md"
                                )
                            ]
                        ),
                        BoxComponent(
                            layout="vertical",
                            background_color="#DBEAFE",
                            corner_radius="md",
                            padding_all="12px",
                            spacing="sm",
                            contents=[
                                TextComponent(
                                    text="MENGENAL ATMOSINFO",
                                    weight="bold",
                                    size="md",
                                    color="#000000"
                                ),
                                TextComponent(
                                    text="Deskripsi ATMOSINFO selengkapnya disini:",
                                    size="xs",
                                    wrap=True
                                ),
                                ButtonComponent(
                                    style="primary",
                                    height="sm",
                                    color="#1C398E",
                                    action=URIAction(
                                        label="Lihat ATMOSINFO",
                                        uri="https://docs.google.com/document/d/1sISZQncRWjkxGBrkwovLo3i-mMC_EOp5BB2skRDVUlM/edit?tab=t.0"
                                    ),
                                    margin="md"
                                )
                            ]
                        ),
                        BoxComponent(
                            layout="vertical",
                            background_color="#DBEAFE",
                            corner_radius="md",
                            padding_all="12px",
                            spacing="sm",
                            contents=[
                                TextComponent(
                                    text="KALENDER PUSAT",
                                    weight="bold",
                                    size="md",
                                    color="#000000"
                                ),
                                TextComponent(
                                    text="Intip Timeline Publikasi Grup Line dibawah:",
                                    size="xs",
                                    wrap=True
                                ),
                                ButtonComponent(
                                    style="primary",
                                    height="sm",
                                    color="#1C398E",
                                    action=URIAction(
                                        label="Lihat Kalender",
                                        uri="https://calendar.google.com/calendar/embed?src=c_aee5d5c10e1ea4f22ce9252b92b378a948f2b43cd03000c3d3c7c1afe1d203ff%40group.calendar.google.com&ctz=Asia%2FJakarta"
                                    ),
                                    margin="md"
                                )
                            ]
                        )
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



