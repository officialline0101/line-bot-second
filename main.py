# main.py
from flask import Flask, request, abort
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.messaging.models import ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError
import os
from dotenv import load_dotenv

# .env 読み込み
load_dotenv()

# 環境変数を取得
ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

# Flask アプリ初期化
app = Flask(__name__)

# LINE Bot SDK の設定（v3対応）
configuration = Configuration(access_token=ACCESS_TOKEN)
api_client = ApiClient(configuration=configuration)
line_bot_api = MessagingApi(api_client)
handler = WebhookHandler(CHANNEL_SECRET)

# Webhookエンドポイント
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)
    print("📩 Webhook受信:", body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError as e:
        print("❌ 署名エラー:", e)
        abort(400)

    return "OK"

from linebot.v3.messaging.models import FlexMessage, BubbleContainer, BoxComponent, TextComponent

@handler.add(MessageEvent)
def handle_message(event):
    if isinstance(event.message, TextMessageContent):
        user_message = event.message.text

        if "試し" in user_message:
            # Flexメッセージを定義
            bubble = BubbleContainer(
                body=BoxComponent(
                    layout="vertical",
                    contents=[
                        TextComponent(text="🌟 試しメッセージだよ 🌟", weight="bold", size="lg"),
                        TextComponent(text="これはFlex Messageのテストだよ〜ん💬", wrap=True)
                    ]
                )
            )
            flex_message = FlexMessage(
                alt_text="Flexメッセージ：試し",
                contents=bubble
            )

            response = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[flex_message]
            )
        elif "こんにちは" in user_message:
            response = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="ギャル参上👠✨")]
            )
        elif "予約" in user_message:
            response = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text="予約ね〜💖空いてるか確認してみるぅ！")]
            )
        else:
            response = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=f"それな〜『{user_message}』って感じ💋")]
            )

        line_bot_api.reply_message(response)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Renderが自動でセットしてくれるPORTを使う！
    app.run(host="0.0.0.0", port=port)
