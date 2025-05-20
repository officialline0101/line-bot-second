# main.py
from flask import Flask, request, abort
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import MessagingApi, Configuration
from linebot.v3.messaging.models import ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError
import os
from dotenv import load_dotenv

# .env 読み込み
load_dotenv()

# 環境変数
ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

# LINE Bot 初期化
configuration = Configuration(access_token=ACCESS_TOKEN)
line_bot_api = MessagingApi(configuration)
handler = WebhookHandler(CHANNEL_SECRET)
app = Flask(__name__)

# Webhookエンドポイント
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)
    print("📩 Webhook body:", body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError as e:
        print("❌ Signature Error:", e)
        abort(400)

    return "OK"

# メッセージイベントを処理
@handler.add(MessageEvent)
def handle_message(event):
    if isinstance(event.message, TextMessageContent):
        user_message = event.message.text
        reply_text = "ギャル参上👠✨" if "こんにちは" in user_message else f"それな〜『{user_message}』って感じ💋"
        response = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=reply_text)]
        )
        line_bot_api.reply_message(response)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Renderが自動でセットしてくれるPORTを使う！
    app.run(host="0.0.0.0", port=port)
