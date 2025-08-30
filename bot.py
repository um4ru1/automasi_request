from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage, 
    BubbleContainer, BoxComponent, TextComponent, ButtonComponent, SeparatorComponent,
    ImageComponent
)
from linebot.models.actions import URIAction
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
    user_message = event.message.text.strip().lower()
    
    if user_message == "mpub":
        flex_message = FlexSendMessage(
            alt_text="Minfo Publikasi",
            contents=BubbleContainer(
                body=BoxComponent(
                    layout='vertical',
                    spacing='md',
                    contents=[
                        TextComponent(
                            text="Kalender Atmosinfo",
                            weight="bold",
                            size="md",
                            wrap=True
                        ),
                        ButtonComponent(
                            style="primary",
                            color="#1C398E",
                            height="sm",
                            action=URIAction(
                                label="Buka Kalender",
                                uri="https://tr.ee/KalenderAtmosInfo"
                            )
                        ),
                        TextComponent(
                            text="Form Pemesanan Jadwal Publikasi Grup Line:",
                            weight="bold",
                            size="md",
                            wrap=True,
                            margin="md"
                        ),
                        ButtonComponent(
                            style="primary",
                            color="#1C398E",
                            height="sm",
                            action=URIAction(
                                label="Isi Form Pemesanan",
                                uri="https://tr.ee/Pemesanan_Publikasi_GrupLine"
                            )
                        ),
                        TextComponent(
                            text="Form Penghapusan Jadwal Publikasi Grup Line:",
                            weight="bold",
                            size="md",
                            wrap=True,
                            margin="md"
                        ),
                        ButtonComponent(
                            style="primary",
                            color="#1C398E",
                            height="sm",
                            action=URIAction(
                                label="Isi Form Penghapusan",
                                uri="https://tr.ee/FormHapusBcLINE"
                            )
                        ),
                    ]
                )
            )
        )
        line_bot_api.reply_message(event.reply_token, flex_message)


    elif user_message == "ai":
        flex_message = FlexSendMessage(
            alt_text="Homepage",
            contents=BubbleContainer(
                hero=ImageComponent(
                    url="https://i.imgur.com/9HUCGEa.jpeg",
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
                                    text="Atmosinfo",
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
                                    text="ARCHIPAIRA",
                                    weight="bold",
                                    size="md",
                                    color="#000000"
                                ),
                                TextComponent(
                                    text="Link pusat yang berisi Media Sosial HMME, Arsip Pusat, SOP, Form Pemesanan, dan Kalender",
                                    size="xs",
                                    wrap=True
                                ),
                                ButtonComponent(
                                    style="primary",
                                    height="sm",
                                    color="#1C398E",
                                    action=URIAction(
                                        label="Buka ARCHIPAIRA",
                                        uri="https://linktr.ee/ARCHIPHAIRA"
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
                                        uri="https://docs.google.com/document/d/1IKzUd2L9vxNCgf-wdOlgigIK_J_GXpgttLxnicck228/edit?usp=sharing"
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
                                    text="ATMOSINFO",
                                    weight="bold",
                                    size="md",
                                    color="#000000"
                                ),
                                TextComponent(
                                    text="Deskripsi Atmosinfo selengkapnya disini:",
                                    size="xs",
                                    wrap=True
                                ),
                                ButtonComponent(
                                    style="primary",
                                    height="sm",
                                    color="#1C398E",
                                    action=URIAction(
                                        label="Lihat Deskripsi",
                                        uri="https://docs.google.com/document/d/1GoUlTPfbiSPuU8QyGn0Rl9oE75cktOuSOhgzCJRy__s/edit?tab=t.0"
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
                                    text="SARAN DAN KRITIK",
                                    weight="bold",
                                    size="md",
                                    color="#000000"
                                ),
                                TextComponent(
                                    text="Tuangkan saran dan kritikmu untuk Atmosinfo melalui Google Form dibawah:",
                                    size="xs",
                                    wrap=True
                                ),
                                ButtonComponent(
                                    style="primary",
                                    height="sm",
                                    color="#1C398E",
                                    action=URIAction(
                                        label="Aku ada Saran/Kritik",
                                        uri="https://docs.google.com/forms/d/e/1FAIpQLSdEwalIGsDaXrWN1VoGOwKYO3tT16yc89eLEBR37kwPt1oIZw/viewform?usp=dialog"
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

    else:
        flex_message = FlexSendMessage(
            alt_text="Keyword tidak ditemukan",
            contents=BubbleContainer(
                body=BoxComponent(
                    layout="vertical",
                    spacing="md",
                    contents=[
                        BoxComponent(
                            layout="horizontal",
                            background_color="#D0E8FF",
                            padding_all="10px",
                            corner_radius="md",
                            contents=[
                                TextComponent(
                                    text="keywordmu\n tidak ditemukan :(",
                                    wrap=True,
                                    weight="bold",
                                    size="xl",
                                    color="#1C398E",
                                    align="center"
                                )
                            ]
                        ),
                        SeparatorComponent(),
                        BoxComponent(
                            layout="vertical",
                            background_color="#D0E8FF",
                            padding_all="10px",
                            corner_radius="md",
                            contents=[
                                TextComponent(
                                    text="Daftar Keyword Tersedia",
                                    size="lg",
                                    weight="bold",
                                    color="#000000",
                                    wrap=True,
                                    margin="sm"
                                ),
                                TextComponent(
                                    text="Keyword Utama",
                                    size="md",
                                    weight="bold",
                                    color="#000000",
                                    wrap=True,
                                    margin="lg"
                                ),
                                TextComponent(
                                    text="ai",
                                    size="sm",
                                    wrap=True,
                                    weight="bold"
                                ),
                                TextComponent(
                                    text="Homepage Atmosinfo, berisi Arsipin, Mengenal BP25, Mengenal Atmosinfo, dan Form Saran Kritik",
                                    size="xs",
                                    wrap=True,
                                    margin="xs"
                                ),
                                TextComponent(
                                    text="Form Request",
                                    size="sm",
                                    weight="bold",
                                    color="#000000",
                                    wrap=True,
                                    margin="lg"
                                ),
                                TextComponent(
                                    text="mpub",
                                    size="sm",
                                    wrap=True,
                                    weight="bold"
                                ),
                                TextComponent(
                                    text="request publikasi grup line",
                                    size="xs",
                                    wrap=True,
                                    margin="xs"
                                ),
                            ]
                        ),
                        SeparatorComponent(),
                        TextComponent(
                            text="Silakan ketik salah satu keyword di atas untuk melihat informasinya.",
                            size="xxs",
                            color="#888888",
                            wrap=True,
                            margin="md"
                        )
                    ]
                )
            )
        )
        
        line_bot_api.reply_message(event.reply_token, flex_message)

@app.route("/notify", methods=["POST"])
def notify_admin():
    data = request.get_json()
    if not data:
        return "Data tidak valid.", 400
        
    print("--- 📥 Data POST Diterima ---")
    print(data)
    print("--------------------------")

    message_text = data.get("message")
    # Mengambil data penerima dengan kunci 'recipient_id'
    recipients = data.get("recipient_id") 

    # Daftar penerima default jika tidak ada yg spesifik
    default_recipients = ["U0e62a4a9406a1a35f4573665d5794bc7"]

    # --- Logika Penentuan Penerima (Sudah Diperbarui) ---
    target_ids_to_notify = []
    if recipients:
        # Jika ada data penerima spesifik yang dikirim
        if isinstance(recipients, list):
            # Jika data adalah sebuah list, gunakan langsung
            target_ids_to_notify = recipients
            print(f"🎯 Target spesifik (multiple) ditemukan: {recipients}")
        else:
            # Jika data adalah string (bukan list), jadikan list berisi satu item
            target_ids_to_notify = [recipients]
            print(f"🎯 Target spesifik (single) ditemukan: {recipients}")
    else:
        # Jika tidak ada, gunakan daftar default
        target_ids_to_notify = default_recipients
        print(f"🎯 Menggunakan target default: {default_recipients}")

    if not message_text:
        print("❌ Gagal: 'message' tidak ditemukan dalam data.")
        return "❌ Gagal: 'message' tidak ditemukan.", 400

    try:
        # Mengirim ke semua target yang sudah ditentukan
        line_bot_api.multicast(target_ids_to_notify, TextSendMessage(text=message_text))
        print(f"✅ Berhasil kirim multicast ke: {target_ids_to_notify}")
        return "✅ Notifikasi berhasil dikirim", 200
    except Exception as e:
        print(f"❌ Gagal kirim multicast: {str(e)}")
        return f"❌ Gagal kirim notifikasi: {str(e)}", 500


if __name__ == "__main__":
    app.run(port=8000)
