from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import textwrap
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
https://tr.ee/KalenderRoseline

Form Pemesanan Jadwal Publikasi Grup Line:
https://tr.ee/FormPesanBcLINE

Form Penghapusan Jadwal Publikasi Grup Line:
https://tr.ee/FormHapusBcLINE
"""
    elif user_message == "rose1":
        reply_text = "fdsafasdfa"
    else:
        reply_text = textwrap.dedent("""\
            SOP BP HMME "ATMOSPHAIRA" 2025/2026
            yang tersedia sementara: melati2
           
            rose1 = SOP Biro Kesekjenan
            rose2 = SOP Departemen Advokasi Keilmuan
            rose3 = SOP Departemen Medkom
            rose4 = SOP Departemen PSDA
            rose5 = SOP Departemen Eksternal
            rose6 = SOP Departemen Internal

            FORM REQUEST
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
            
            """)

    # Kirim balasan ke user
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

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
        "C057c315ef3883896b67280c4aa97066b"
    ]

    try:
        line_bot_api.multicast(user_ids, TextSendMessage(text=message_text))
        print("✅ Berhasil kirim multicast!")
        return "✅ Notifikasi berhasil dikirim", 200
    except Exception as e:
        print(f"❌ Gagal kirim multicast: {str(e)}")
        return f"❌ Gagal kirim notifikasi: {str(e)}", 500



