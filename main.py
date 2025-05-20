from flask import Flask, request, abort
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import MessagingApi, Configuration
from linebot.v3.messaging.models import (
    ReplyMessageRequest,
    TextMessage,
    FlexMessage
)
from linebot.v3.exceptions import InvalidSignatureError
import os
import json
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()
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

    if user_message == "試し":
        # Flex Message JSONをPython辞書形式で用意
        flex_content = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": "https://developers-resource.landpress.line.me/fx/img/01_1_cafe.png",
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover",
                "action": {
                    "type": "uri",
                    "uri": "https://line.me/"
                }
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "Brown Cafe",
                        "weight": "bold",
                        "size": "xl"
                    },
                    {
                        "type": "box",
                        "layout": "baseline",
                        "margin": "md",
                        "contents": [
                            *[{"type": "icon", "size": "sm", "url": "https://developers-resource.landpress.line.me/fx/img/review_gold_star_28.png"} for _ in range(4)],
                            {"type": "icon", "size": "sm", "url": "https://developers-resource.landpress.line.me/fx/img/review_gray_star_28.png"},
                            {
                                "type": "text",
                                "text": "4.0",
                                "size": "sm",
                                "color": "#999999",
                                "margin": "md",
                                "flex": 0
                            }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {"type": "text", "text": "Place", "color": "#aaaaaa", "size": "sm", "flex": 1},
                                    {"type": "text", "text": "Flex Tower, 7-7-4 Midori-ku, Tokyo", "wrap": True, "color": "#666666", "size": "sm", "flex": 5}
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {"type": "text", "text": "Time", "color": "#aaaaaa", "size": "sm", "flex": 1},
                                    {"type": "text", "text": "10:00 - 23:00", "wrap": True, "color": "#666666", "size": "sm", "flex": 5}
                                ]
                            }
                        ]
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": "CALL",
                            "uri": "https://line.me/"
                        }
                    },
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": "WEBSITE",
                            "uri": "https://line.me/"
                        }
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [],
                        "margin": "sm"
                    }
                ],
                "flex": 0
            }
        }

        response = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[
                FlexMessage(
                    alt_text="Brown Cafeの情報です☕️",
                    contents=flex_content
                )
            ]
        )
    else:
        # 通常テキスト返信
        response = ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=f"『{user_message}』って感じだね！")]
        )

    line_bot_api.reply_message(response)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Renderが自動でセットしてくれるPORTを使う！
    app.run(host="0.0.0.0", port=port)
