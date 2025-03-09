from flask import Flask, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import logging
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, FlexSendMessage
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
try:
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_json = json.loads(GOOGLE_CREDENTIALS)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID).sheet1
    logging.info("Terhubung ke Google Sheets.")
except Exception as e:
    logging.error(f"Error Google Sheets: {e}")
    raise

# Konfigurasi Google Calendar
try:
    calendar_service = build("calendar", "v3", credentials=creds)
    logging.info("Terhubung ke Google Calendar.")
except Exception as e:
    logging.error(f"Error Google Calendar: {e}")
    raise

# Zona waktu Jakarta
jakarta_tz = pytz.timezone("Asia/Jakarta")

def get_available_slots():
    now = datetime.now(jakarta_tz).isoformat()
    try:
        events_result = calendar_service.events().list(
            calendarId=GOOGLE_CALENDAR_ID, timeMin=now, maxResults=20, singleEvents=True,
            orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])
    except Exception as e:
        logging.error(f"Error mendapatkan jadwal dari Google Calendar: {e}")
        return []

    booked_slots = {(event['start']['dateTime'][:10], event['start']['dateTime'][11:16]) for event in events if 'dateTime' in event['start']}

    available_slots = []
    for day_offset in range(7):  # 7 hari ke depan
        date = (datetime.now(jakarta_tz) + timedelta(days=day_offset)).strftime("%Y-%m-%d")
        for hour in range(7, 23, 3):  # Interval 3 jam
            time_slot = f"{hour:02}:00"
            if (date, time_slot) not in booked_slots:
                available_slots.append((date, time_slot))

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

        # Membuat Flex Message untuk pemilihan jadwal
        flex_contents = []
        for date, time_slot in available_slots[:10]:  # Maksimal 10 pilihan
            flex_contents.append({
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": f"{date} {time_slot}", "weight": "bold", "size": "lg"},
                        {"type": "button", "style": "primary", "action": {"type": "message", "label": "Pilih", "text": f"Pilih {date} {time_slot}"}}
                    ]
                }
            })

        flex_message = FlexSendMessage(
            alt_text="Silakan pilih jadwal:",
            contents={"type": "carousel", "contents": flex_contents}
        )
        line_bot_api.reply_message(event.reply_token, flex_message)
    
    elif user_text.lower().startswith("pilih"):
        try:
            parts = user_text.split(" ", 3)
            if len(parts) < 3:
                raise ValueError("Format salah")
            selected_date = parts[1]
            selected_time = parts[2]
            
            available_slots = get_available_slots()
            if (selected_date, selected_time) not in available_slots:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Jadwal tidak valid atau sudah diambil."))
                return
            
            selected_datetime = jakarta_tz.localize(datetime.strptime(f"{selected_date} {selected_time}", "%Y-%m-%d %H:%M"))
            start_time = selected_datetime.isoformat()
            end_time = (selected_datetime + timedelta(hours=1)).isoformat()

            # Simpan ke Google Calendar
            event_body = {
                "summary": f"Booking oleh {user_id}",
                "start": {"dateTime": start_time, "timeZone": "Asia/Jakarta"},
                "end": {"dateTime": end_time, "timeZone": "Asia/Jakarta"}
            }
            calendar_service.events().insert(calendarId=GOOGLE_CALENDAR_ID, body=event_body).execute()
            
            # Simpan ke Google Sheets
            sheet.append_row([user_id, selected_date, selected_time])
            
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"Jadwal {selected_date} {selected_time} telah dipesan."))
        except Exception as e:
            logging.error(f"Error: {e}")
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Format salah."))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
