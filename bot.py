import os
import json
import gspread
from flask import Flask, request, abort, render_template
from google.oauth2 import service_account
from googleapiclient.discovery import build
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, FlexSendMessage, PostbackEvent
)
from datetime import datetime, timedelta
import pytz

# Load environment variables from Koyeb
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
GOOGLE_CREDENTIALS = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
LIFF_URL = "https://your-liff-app-url"  # Ganti dengan URL LIFF kamu

# Define Google API Scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/calendar"
]

# Google Authentication
credentials = service_account.Credentials.from_service_account_info(
    GOOGLE_CREDENTIALS, scopes=SCOPES
)

# Initialize Google Services
gspread_client = gspread.authorize(credentials)
calendar_service = build("calendar", "v3", credentials=credentials)

# Access Google Sheets
try:
    sheet = gspread_client.open_by_key(SPREADSHEET_ID).sheet1
except Exception as e:
    print(f"Error accessing Google Sheets: {e}")

# Initialize Flask App
app = Flask(__name__)

# Initialize LINE API
line_bot_api = LineBotApi(LINE_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    if data.startswith("action=select_date"):
        selected_datetime = event.postback.params["datetime"]
        user_id = event.source.user_id
        store_event(user_id, selected_datetime, "Pesan belum diinput")
        line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text=f"Jadwal disimpan: {selected_datetime}\nSilakan klik tombol Ketik Pesan untuk memasukkan pesan broadcast.")
        )

@app.route("/submit_message", methods=["POST"])
def submit_message():
    data = request.json
    user_id = data.get("user_id")
    message = data.get("message")
    update_message(user_id, message)
    return {"status": "success", "message": "Pesan berhasil disimpan."}

def store_event(user_id, selected_datetime, message):
    try:
        start_time = datetime.fromisoformat(selected_datetime)
        end_time = start_time + timedelta(minutes=1)
        
        event = {
            "summary": f"Broadcast oleh {user_id}",
            "start": {"dateTime": start_time.isoformat(), "timeZone": "Asia/Jakarta"},
            "end": {"dateTime": end_time.isoformat(), "timeZone": "Asia/Jakarta"}
        }
        calendar_service.events().insert(calendarId=GOOGLE_CALENDAR_ID, body=event).execute()
        
        sheet.append_row([user_id, selected_datetime, message])
    except Exception as e:
        print(f"Error storing event: {e}")

def update_message(user_id, message):
    try:
        cell = sheet.find(user_id)
        sheet.update_cell(cell.row, 3, message)
    except Exception as e:
        print(f"Error updating message: {e}")

def create_flex_message():
    flex_content = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "Form Input Jadwal", "weight": "bold", "size": "xl"},
                {"type": "text", "text": "Silakan pilih waktu dan masukkan pesan Anda.", "size": "md", "wrap": True},
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "contents": [
                        {
                            "type": "text",
                            "text": "Pilih Waktu Broadcast:",
                            "weight": "bold"
                        },
                        {
                            "type": "button",
                            "style": "primary",
                            "color": "#1DB446",
                            "action": {
                                "type": "datetimepicker",
                                "label": "Pilih Waktu",
                                "data": "action=select_date",
                                "mode": "datetime"
                            }
                        },
                        {
                            "type": "text",
                            "text": "Masukkan Pesan Broadcast:",
                            "weight": "bold",
                            "margin": "md"
                        },
                        {
                            "type": "button",
                            "style": "secondary",
                            "color": "#AAAAAA",
                            "action": {
                                "type": "uri",
                                "label": "Ketik Pesan",
                                "uri": LIFF_URL
                            }
                        }
                    ]
                }
            ]
        }
    }
    return FlexSendMessage(
        alt_text="Form Input Jadwal",
        contents=flex_content
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
