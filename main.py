# main.py
from flask import Flask, request, abort
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import MessagingApi, Configuration
from linebot.v3.messaging.models import ReplyMessageRequest, TextMessage
from linebot.v3.exceptions import InvalidSignatureError
import os
from dotenv import load_dotenv

load_dotenv()

# 環境変数
ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

# LINE APIの設定
configuration = Configuration(access_token=ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)
app = Flask(__name__)
line_bot_api = MessagingApi(configuration)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    print(f"📩 Webhook受信: {body}")

    try:
        handler.handle(body, signature)
    except InvalidSignatureError as e:
        print("❌ 署名エラー:", e)
        abort(400)
    return 'OK'

@handler.add(event_type="message")
def handle_message(event):
    user_message = event.message.text
    reply_text = "ギャル参上👠✨" if "こんにちは" in user_message else f"それな〜『{user_message}』って感じ💋"
    response = ReplyMessageRequest(
        reply_token=event.reply_token,
        messages=[TextMessage(text=reply_text)]
    )
    line_bot_api.reply_message(response)

if __name__ == "__main__":
    app.run(debug=True)
