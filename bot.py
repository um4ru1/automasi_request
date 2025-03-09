import os
import json
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, FlexSendMessage, PostbackEvent
from flask import Flask, request, abort
from googleapiclient.discovery import build
from google.oauth2 import service_account

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
credentials = service_account.Credentials.from_service_account_info(
    GOOGLE_CREDENTIALS, scopes=["https://www.googleapis.com/auth/calendar"]
)
service = build("calendar", "v3", credentials=credentials)

# Google Sheets Authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(GOOGLE_CREDENTIALS, scope)
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

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    if event.message.text == "!jadwal":
        flex_message = create_flex_message()
        line_bot_api.reply_message(event.reply_token, flex_message)

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
                        },
                        {
                            "type": "button",
                            "style": "secondary",
                            "action": {
                                "type": "message",
                                "label": "Ketik Pesan Broadcast",
                                "text": "Masukkan pesan broadcast: "
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
    if data.startswith("action=select_date"):
        selected_datetime = event.postback.params["datetime"]
        user_id = event.source.user_id
        store_event(user_id, selected_datetime)
        line_bot_api.reply_message(event.reply_token, TextMessage(text=f"Jadwal disimpan: {selected_datetime}"))

def store_event(user_id, selected_datetime):
    event = {
        "summary": f"Booking oleh {user_id}",
        "start": {"dateTime": selected_datetime, "timeZone": "Asia/Jakarta"},
        "end": {"dateTime": selected_datetime, "timeZone": "Asia/Jakarta"}
    }
    service.events().insert(calendarId=GOOGLE_CALENDAR_ID, body=event).execute()
    sheet.append_row([user_id, selected_datetime, "Pesan pending..."])  # Tempat penyimpanan pesan

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
