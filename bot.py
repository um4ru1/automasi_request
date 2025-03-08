from flask import Flask, request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import logging
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction
from linebot.exceptions import InvalidSignatureError

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

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature", 400

    return "OK", 200

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    user_text = event.message.text.strip()
    user_id = event.source.user_id
    
    if user_text.lower() == "!jadwal":
        existing_data = sheet.get_all_records()
        booked_slots = {row["Jadwal"] for row in existing_data if "Jadwal" in row}
        
        all_slots = [f"{hour}:00" for hour in range(7, 23, 3)]
        available_slots = [slot for slot in all_slots if slot not in booked_slots]
        
        if not available_slots:
            reply_text = "Semua jadwal sudah terisi."
        else:
            buttons = [QuickReplyButton(action=MessageAction(label=slot, text=f"Pilih {slot}")) for slot in available_slots]
            reply_text = "Silakan pilih jadwal yang tersedia:"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text, quick_reply=QuickReply(items=buttons)))
            return
    
    elif user_text.startswith("Pilih "):
        selected_time = user_text.replace("Pilih ", "").strip()
        existing_data = sheet.get_all_records()
        booked_slots = {row["Jadwal"] for row in existing_data if "Jadwal" in row}
        
        if selected_time in booked_slots:
            reply_text = "Jadwal sudah terisi, silakan pilih waktu lain."
        else:
            sheet.append_row([user_id, selected_time])
            reply_text = f"Jadwal {selected_time} berhasil dipesan!"
    else:
        reply_text = "Ketik !jadwal untuk melihat jadwal yang tersedia."
    
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
