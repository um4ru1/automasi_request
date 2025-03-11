import os
import json
import gspread
from flask import Flask, request, abort
from google.oauth2 import service_account
from googleapiclient.discovery import build
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, FlexSendMessage, PostbackEvent
)

# Load environment variables from Koyeb
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
GOOGLE_CREDENTIALS = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

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

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user_id = event.source.user_id
    message_text = event.message.text
    
    if message_text == "!jadwal":
        flex_message = create_flex_message()
        line_bot_api.reply_message(event.reply_token, flex_message)
    else:
        # Simpan pesan ke Google Sheets untuk user yang sudah memilih jadwal
        update_message(user_id, message_text)
        line_bot_api.reply_message(event.reply_token, TextMessage(text=f"Pesan Broadcast:\n{message_text}"))

@handler.add(PostbackEvent)
def handle_postback(event):
    data = event.postback.data
    if data.startswith("action=select_date"):
        selected_datetime = event.postback.params["datetime"]
        user_id = event.source.user_id
        store_event(user_id, selected_datetime, "Pesan belum diinput")
        line_bot_api.reply_message(event.reply_token, TextMessage(text=f"Jadwal disimpan: {selected_datetime}\nSilakan ketik pesan broadcast Anda."))

def store_event(user_id, selected_datetime, message):
    try:
        event = {
            "summary": f"Booking oleh {user_id}",
            "start": {"dateTime": selected_datetime, "timeZone": "Asia/Jakarta"},
            "end": {"dateTime": selected_datetime, "timeZone": "Asia/Jakarta"}
        }
        calendar_service.events().insert(calendarId=GOOGLE_CALENDAR_ID, body=event).execute()
        
        sheet.append_row([user_id, selected_datetime, message])
    except Exception as e:
        print(f"Error storing event: {e}")

def update_message(user_id, message):
    try:
        cell = sheet.find(user_id)
        sheet.update_cell(cell.row, 3, message)  # Update kolom pesan
    except Exception as e:
        print(f"Error updating message: {e}")

def create_flex_message():
    flex_content = {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "Pilih Jadwal & Masukkan Pesan", "weight": "bold", "size": "xl"},
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "md",
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
                        },
                        {
                            "type": "text",
                            "text": "📝 Masukkan pesan broadcast di bawah:",
                            "weight": "bold",
                            "margin": "md"
                        },
                        {
                            "type": "button",
                            "style": "primary",
                            "color": "#00B900",
                            "action": {
                                "type": "message",
                                "label": "Kirim Pesan",
                                "text": "Pesan Broadcast:"
                            }
                        }
                    ]
                }
            ]
        }
    }
    return FlexSendMessage(alt_text="Form Input Jadwal", contents=flex_content)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
