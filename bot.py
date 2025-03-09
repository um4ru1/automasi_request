from flask import Flask, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import logging
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction
from linebot.exceptions import InvalidSignatureError
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pytz

# Konfigurasi Logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Load konfigurasi dari environment variables
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

if not all([LINE_ACCESS_TOKEN, LINE_CHANNEL_SECRET, SPREADSHEET_ID, GOOGLE_CREDENTIALS, GOOGLE_CALENDAR_ID]):
    raise ValueError("Environment variables tidak lengkap! Periksa kembali konfigurasi di Koyeb.")

# Konfigurasi Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_json = json.loads(GOOGLE_CREDENTIALS)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# Konfigurasi Google Calendar
calendar_service = build("calendar", "v3", credentials=creds)

# Zona waktu Jakarta
jakarta_tz = pytz.timezone("Asia/Jakarta")


def get_available_slots():
    now = datetime.now(jakarta_tz).isoformat()
    events_result = calendar_service.events().list(
        calendarId=GOOGLE_CALENDAR_ID, timeMin=now, maxResults=20, singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    
    booked_slots = {event['start']['dateTime'][11:16] for event in events if 'dateTime' in event['start']}
    
    available_slots = []
    for hour in range(7, 23, 3):  # Interval 3 jam (7:00, 10:00, 13:00, ..., 22:00)
        time_slot = f"{hour:02}:00"
        if time_slot not in booked_slots:
            available_slots.append(time_slot)
    
    return available_slots


# Konfigurasi LINE API
line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)


@app.route("/")
def home():
    return "LINE Bot is running!", 200


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)
    logging.info(f"Request Body: {body}")
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logging.error("Invalid Signature!")
        return "Invalid signature", 400
    return "OK", 200


@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user_text = event.message.text.strip()
    user_id = event.source.user_id

    if user_text.lower() == "!jadwal":
        available_slots = get_available_slots()

        if not available_slots:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Tidak ada jadwal kosong."))
            return

        # Membuat Quick Reply Buttons untuk pemilihan jadwal
        quick_reply_buttons = [
            QuickReplyButton(action=MessageAction(label=slot, text=f"Pilih {i+1} ")) for i, slot in enumerate(available_slots)
        ]
        quick_reply = QuickReply(items=quick_reply_buttons)

        reply_message = TextSendMessage(
            text="Silakan pilih jadwal yang tersedia:",
            quick_reply=quick_reply
        )
        line_bot_api.reply_message(event.reply_token, reply_message)

    elif user_text.lower().startswith("pilih"):
        try:
            parts = user_text.split(" ", 2)
            if len(parts) < 3:
                raise ValueError("Format salah")
            slot_index = int(parts[1]) - 1
            broadcast_text = parts[2]
            available_slots = get_available_slots()

            if slot_index < 0 or slot_index >= len(available_slots):
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Nomor jadwal tidak valid."))
                return

            selected_time = available_slots[slot_index]
            now_jakarta = datetime.now(jakarta_tz)
            date_today = now_jakarta.strftime("%Y-%m-%d")

            selected_datetime = jakarta_tz.localize(datetime.strptime(f"{date_today} {selected_time}", "%Y-%m-%d %H:%M"))
            start_time = selected_datetime.isoformat()
            end_time = (selected_datetime + timedelta(hours=1)).isoformat()

            # Cek apakah jadwal sudah ada di Google Sheets
            existing_records = sheet.get_all_values()
            for row in existing_records:
                if row[1] == selected_time:  # Kolom kedua adalah waktu
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Jadwal ini sudah diambil, silakan pilih yang lain."))
                    return

            # Simpan ke Google Calendar
            event_body = {
                "summary": f"Booking oleh {user_id}",
                "start": {"dateTime": start_time, "timeZone": "Asia/Jakarta"},
                "end": {"dateTime": end_time, "timeZone": "Asia/Jakarta"}
            }

            try:
                calendar_service.events().insert(calendarId=GOOGLE_CALENDAR_ID, body=event_body).execute()
            except Exception as e:
                logging.error(f"Google Calendar Error: {e}")
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Terjadi kesalahan saat menyimpan jadwal. Silakan coba lagi nanti."))
                return

            # Simpan ke Google Sheets
            sheet.append_row([user_id, selected_time, broadcast_text])

            line_bot_api.reply_message(
                event.reply_token, 
                TextSendMessage(text=f"Jadwal {selected_time} telah dipesan dengan pesan: {broadcast_text}")
            )

        except Exception as e:
            logging.error(f"Error: {e}")
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Format salah. Gunakan: Pilih <nomor jadwal> <pesan broadcast>."))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
