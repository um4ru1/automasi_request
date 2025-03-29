from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

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
    user_message = event.message.text.strip().lower()  # Ambil teks dan ubah ke huruf kecil

    # Cek input dari user dan berikan balasan yang sesuai
    if user_message == "melati2":
        reply_text = """GOOGLE CALENDAR:
https://calendar.google.com/calendar/u/0?cid=ZTE1NGNhMGMwYjYxOWE5M2YzOGIyODVkMjI0ODA5ZTJiZTNhNzkzMWM0Y2RjMDU3ZWQzNjliYzdkM2Q3NTI4NEBncm91cC5jYWxlbmRhci5nb29nbGUuY29t

FORM PENGHAPUSAN JADWAL:
https://forms.gle/dK4Xa4FXVWQZ6coH8

FORM INPUT BROADCAST:
https://forms.gle/tp3SST7qEjGLSTwR7
"""
    elif user_message == "rose1":
        reply_text = "fdsafasdfa"
    else:
        reply_text = (
            """SOP BP HMME "ATMOSPHAIRA" 2025/2026
            yang tersedia sementara: melati2
            Berikut beberapa pilihan:
            rose1 = SOP Biro Kesekjenan
            rose2 = SOP Departemen Advokasi Keilmuan
            rose3 = SOP Departemen Medkom
            rose4 = SOP Departemen PSDA
            rose5 = SOP Departemen Eksternal
            rose6 = SOP Departemen Internal

            FORM REQUEST\n
            melati1 = Pengajuan Agenda
            melati2 = Roseline(Publikasi grup line)
            melati3 = Rosepub(Media Atmos, publikasi ig, tiktok dkk)
            melati4 = Rosemading(mading atmos offline)
            melati5 = Rosedesain(Pemesanan Desain)
            melati6 = Pengajuan SKA
            melati7 = Permohonan bimbingan lomba
            melati8 = kian(kepoin alumni)
            melati9 = kunjungan bareng atmosphaira
                 
            KALENDER
            kal1 = KalenderRoseline
            kal2 = Kalendermelati
            """
            
        )

    # Kirim balasan ke user
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    app.run(port=8000)
