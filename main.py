from flask import Flask, request, abort
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import MessagingApi, Configuration
from linebot.v3.messaging.models import (
    ReplyMessageRequest,
    FlexMessage,
    FlexContainer,
    BubbleContainer,
    BoxComponent,
    TextComponent,
    ImageComponent,
    ButtonComponent,
    URIAction,
    MessageAction
)
from linebot.v3.exceptions import InvalidSignatureError
import os
from dotenv import load_dotenv

# .env 読み込み
load_dotenv()

# 環境変数
ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

# LINE設定
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

    # Flex Message（ギャル風のおしゃれなメッセージ）
    bubble = BubbleContainer(
        body=BoxComponent(
            layout="vertical",
            contents=[
                TextComponent(text="👠 ギャル参上！", weight="bold", size="xl", color="#D81B60"),
                TextComponent(text=f"あんた『{user_message}』って送ったね💋", size="sm", color="#555555", wrap=True),
            ]
        ),
        footer=BoxComponent(
            layout="horizontal",
            spacing="sm",
            contents=[
                ButtonComponent(
                    style="primary",
                    height="sm",
                    action=MessageAction(label="ありがと〜💖", text="ありがと！")
                ),
                ButtonComponent(
                    style="link",
                    height="sm",
                    action=URIAction(label="おすすめ見る👀", uri="https://line.me")
                )
            ]
        )
    )

    flex_message = FlexMessage(
        alt_text="ギャルからのメッセージです👠",
        contents=bubble
    )

    response = ReplyMessageRequest(
        reply_token=event.reply_token,
        messages=[flex_message]
    )
    line_bot_api.reply_message(response)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Renderが自動でセットしてくれるPORTを使う！
    app.run(host="0.0.0.0", port=port)
