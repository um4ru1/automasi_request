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

# Konfigurasi Logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Load konfigurasi dari environment variables
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")

# Pastikan semua environment variables tersedia
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

def get_available_slots():
    now = datetime.utcnow().isoformat() + 'Z'
    events_result = calendar_service.events().list(
        calendarId=GOOGLE_CALENDAR_ID, timeMin=now, maxResults=20, singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])
    booked_slots = {event['start']['dateTime'][11:16] for event in events if 'dateTime' in event['start']}
    
    available_slots = []
    for hour in range(7, 23, 3):
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

    logging.info("Menerima request dari LINE")
    logging.info(f"Request Body: {body}")

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logging.error("Invalid Signature!")
        return "Invalid signature", 400

    return "OK", 200

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user_text = event.message.text
    user_id = event.source.user_id
    
    if user_text.lower() == "!jadwal":
        available_slots = get_available_slots()
        
        if not available_slots:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Tidak ada jadwal kosong."))
            return
        
        quick_reply_items = [QuickReplyButton(action=MessageAction(label=slot, text=f"Pilih {slot}")) for slot in available_slots]
        quick_reply = QuickReply(items=quick_reply_items)
        reply_message = TextSendMessage(text="Pilih jam yang tersedia:", quick_reply=quick_reply)
        line_bot_api.reply_message(event.reply_token, reply_message)
    
    elif user_text.lower().startswith("pilih"):
        selected_time = user_text.split(" ")[1]
        date_today = datetime.utcnow().strftime("%Y-%m-%d")
        start_time = f"{date_today}T{selected_time}:00Z"
        end_time = (datetime.strptime(selected_time, "%H:%M") + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:00Z")
        
        event_body = {
            "summary": f"Booking oleh {user_id}",
            "start": {"dateTime": start_time, "timeZone": "Asia/Jakarta"},
            "end": {"dateTime": end_time, "timeZone": "Asia/Jakarta"}
        }
        calendar_service.events().insert(calendarId=GOOGLE_CALENDAR_ID, body=event_body).execute()
        
        sheet.append_row([user_id, selected_time, "Pesan kosong"])
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=f"Jadwal {selected_time} telah dipesan. Silakan ketik teks tambahan."))
    
    else:
        user_data = sheet.get_all_values()
        for i, row in enumerate(user_data):
            if row[0] == user_id and row[2] == "Pesan kosong":
                sheet.update_cell(i+1, 3, user_text)
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Pesan telah disimpan bersama jadwal Anda!"))
                return
        
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Silakan pilih jadwal terlebih dahulu dengan !jadwal"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
