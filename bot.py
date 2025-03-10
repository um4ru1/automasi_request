import os
import json
import datetime
import gspread
from google.oauth2.service_account import Credentials
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, FlexSendMessage, PostbackEvent
from flask import Flask, request, abort
from googleapiclient.discovery import build

# Load environment variables
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
GOOGLE_CREDENTIALS = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

# Initialize LINE API
line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Google Calendar Authentication
credentials = Credentials.from_service_account_info(
    GOOGLE_CREDENTIALS, scopes=["https://www.googleapis.com/auth/calendar"]
)
service = build("calendar", "v3", credentials=credentials)

# Google Sheets Authentication
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_info(GOOGLE_CREDENTIALS, scopes=scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

app = Flask(__name__)

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

# Menyimpan data sementara untuk user
user_data = {}

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user_id = event.source.user_id
    text = event.message.text

    # Jika user mengetik "!jadwal", kirim form
    if text == "!jadwal":
        flex_message = create_flex_message()
        line_bot_api.reply_message(event.reply_token, flex_message)

    # Jika user mengetik teks setelah memilih waktu, simpan ke Google Sheets
    elif user_id in user_data and "selected_datetime" in user_data[user_id]:
        selected_datetime = user_data[user_id]["selected_datetime"]
        save_to_sheets(user_id, selected_datetime, text)
        save_to_calendar(user_id, selected_datetime)
        line_bot_api.reply_message(event.reply_token, TextMessage(text="✅ Jadwal dan pesan telah disimpan!"))
        del user_data[user_id]  # Hapus data user setelah disimpan

def create_flex_message():
    flex_content = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "Pilih Jadwal", "weight": "bold", "size": "xl"},
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "button",
                            "style": "primary",
                            "action": {
                                "type": "datetimepicker",
                                "label": "Pilih Tanggal & Waktu",
                                "data": "action=select_date",
                                "mode": "datetime"
                            }
                        }
                    ]
                }
            ]
        }
    }
    return FlexSendMessage(alt_text="Form Input Jadwal", contents=flex_content)

@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    user_id = event.source.user_id

    if data.startswith("action=select_date"):
        selected_datetime = event.postback.params["datetime"]
        user_data[user_id] = {"selected_datetime": selected_datetime}
        line_bot_api.reply_message(event.reply_token, TextMessage(text="📌 Silakan ketik pesan broadcast Anda."))

def save_to_calendar(user_id, selected_datetime):
    event = {
        "summary": f"Booking oleh {user_id}",
        "start": {"dateTime": selected_datetime, "timeZone": "Asia/Jakarta"},
        "end": {"dateTime": selected_datetime, "timeZone": "Asia/Jakarta"}
    }
    service.events().insert(calendarId=GOOGLE_CALENDAR_ID, body=event).execute()

def save_to_sheets(user_id, selected_datetime, message):
    sheet.append_row([user_id, selected_datetime, message])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
