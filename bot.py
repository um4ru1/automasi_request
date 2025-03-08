from flask import Flask, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import logging
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError

# Konfigurasi Logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

# Load konfigurasi dari environment variables
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
GOOGLE_CREDENTIALS = os.getenv("GOOGLE_CREDENTIALS")

# Pastikan semua environment variables tersedia
if not all([LINE_ACCESS_TOKEN, LINE_CHANNEL_SECRET, SPREADSHEET_ID, GOOGLE_CREDENTIALS]):
    raise ValueError("Environment variables tidak lengkap! Periksa kembali konfigurasi di Koyeb.")

# Konfigurasi Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_json = json.loads(GOOGLE_CREDENTIALS)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

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

    logging.info(f"Pesan diterima dari {user_id}: {user_text}")

    # Periksa apakah Google Sheet memiliki header
    existing_data = sheet.get_all_records()
    if len(existing_data) == 0:
        logging.info("Sheet kosong, menambahkan header...")
        sheet.append_row(["User ID", "Message"])
        existing_data = sheet.get_all_records()

    # Periksa apakah pesan sudah ada
    for row in existing_data:
        if row["User ID"] == user_id and row["Message"] == user_text:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Pesan sudah tercatat!"))
            return

    # Simpan ke Google Sheets
    sheet.append_row([user_id, user_text])
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text="Pesan disimpan!"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
