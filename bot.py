from flask import Flask, request, jsonify
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import requests

app = Flask(__name__)

# Konfigurasi Google Sheets
SHEET_NAME = "auto_message"
SCOPES = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# Load kredensial Google Sheets dari file JSON
cred_json = json.loads(os.getenv("GOOGLE_SHEETS_CREDENTIALS"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(cred_json, SCOPES)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# Token akses LINE
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")

@app.route("/callback", methods=["POST"])
def callback():
    body = request.get_json()
    events = body.get("events", [])
    
    for event in events:
        if event.get("type") == "message" and "text" in event["message"]:
            user_id = event["source"]["userId"]
            message_text = event["message"]["text"]
            
            # Simpan ke Google Sheets
            sheet.append_row([user_id, message_text])
            
            # Kirim balasan
            reply_message(event["replyToken"], "Pesan Anda telah disimpan!")
    
    return jsonify({"status": "success"})


def reply_message(reply_token, text):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    data = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}]
    }
    requests.post(url, headers=headers, json=data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
