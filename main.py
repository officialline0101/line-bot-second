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

# .env 読み込み
load_dotenv()
ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

# Flask 初期化
app = Flask(__name__)

# LINE API 初期化
configuration = Configuration(access_token=ACCESS_TOKEN)
api_client = ApiClient(configuration=configuration)
line_bot_api = MessagingApi(api_client)
handler = WebhookHandler(CHANNEL_SECRET)

# Flexメッセージ読み込み関数（キーワード検索）
def get_flex_json_by_keyword(keyword):
    try:
        with open("./flex_messages.json", "r", encoding="utf-8") as f:
            all_flex = json.load(f)
            return all_flex.get(keyword)
    except Exception as e:
        print(f"❌ Flexメッセージ読み込みエラー: {e}")
        return None

# Webhook エンドポイント
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)
    print("📩 Webhook受信:", body)

    if signature:
        # LINE公式からのWebhook (署名あり)
        try:
            handler.handle(body, signature)
        except InvalidSignatureError as e:
            print("❌ 署名エラー:", e)
            abort(400)
    else:
        # GASやその他システムからのWebhook (署名なし)
        try:
            event_data = json.loads(body)
            for event in event_data.get("events", []):
                if event.get("type") == "message" and event["message"]["type"] == "text":
                    user_message = event["message"]["text"].strip()
                    reply_token = event["replyToken"]

                    flex_data = get_flex_json_by_keyword(user_message)
                    if flex_data:
                        try:
                            message = FlexMessage(
                                alt_text=f"{user_message}のFlexメッセージ",
                                contents=FlexContainer.from_dict(flex_data)
                            )
                        except Exception as e:
                            print("❌ Flex変換エラー:", e)
                            message = TextMessage(text="Flexメッセージの変換に失敗しました。")
                    else:
                        message = TextMessage(text=f"『{user_message}』に対応するメッセージが見つかりませんでした。")

                    response = ReplyMessageRequest(
                        reply_token=reply_token,
                        messages=[message]
                    )
                    line_bot_api.reply_message(response)
        except Exception as e:
            print("❌ GASからのWebhook処理エラー:", e)

    return "OK"

# handler 経由（署名ありの場合）の処理
@handler.add(MessageEvent)
def handle_message(event):
    if isinstance(event.message, TextMessageContent):
        user_message = event.message.text.strip()

        flex_data = get_flex_json_by_keyword(user_message)

        if flex_data:
            try:
                message = FlexMessage(
                    alt_text=f"{user_message}のFlexメッセージ",
                    contents=FlexContainer.from_dict(flex_data)
                )
            except Exception as e:
                print("❌ Flex変換エラー:", e)
                message = TextMessage(text="Flexメッセージの変換に失敗しました。")
        else:
            message = TextMessage(text=f"『{user_message}』に対応するメッセージが見つかりませんでした。")

        response = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[message]
        )
        line_bot_api.reply_message(response)

# アプリ起動
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
