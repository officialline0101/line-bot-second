from flask import Flask, request, abort
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.messaging.models import (
    ReplyMessageRequest,
    TextMessage,
    FlexMessage,
    FlexContainer
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError

import os
import json
from dotenv import load_dotenv

# .env読み込み
load_dotenv()
ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

# Flask初期化
app = Flask(__name__)

# LINE設定
configuration = Configuration(access_token=ACCESS_TOKEN)
api_client = ApiClient(configuration=configuration)
line_bot_api = MessagingApi(api_client)
handler = WebhookHandler(CHANNEL_SECRET)

# 複数Flexを1ファイルから読み込む関数
def get_flex_json_by_keyword(keyword):
    try:
        with open("./flex_messages.json", "r", encoding="utf-8") as f:
            all_flex = json.load(f)
            return all_flex.get(keyword)
    except Exception as e:
        print(f"❌ Flexメッセージ読み込みエラー: {e}")
        return None

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

# メッセージ受信
@handler.add(MessageEvent)
def handle_message(event):
    if isinstance(event.message, TextMessageContent):
        user_message = event.message.text.strip()

        flex_data = get_flex_json_by_keyword(user_message)

        if flex_data:
            try:
                response = ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[
                        FlexMessage(
                            alt_text=f"{user_message}のFlexメッセージ",
                            contents=FlexContainer.from_dict(flex_data)  # ← 型に変換
                        )
                    ]
                )
            except Exception as e:
                print("❌ Flex変換エラー:", e)
                response = ReplyMessageRequest(
                    reply_token=event.reply_token,
                    messages=[TextMessage(text="Flexメッセージの変換に失敗しました。")]
                )
        else:
            response = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[TextMessage(text=f"『{user_message}』に対応するメッセージが見つかりませんでした。")]
            )

        line_bot_api.reply_message(response)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Renderが自動でセットしてくれるPORTを使う！
    app.run(host="0.0.0.0", port=port)
