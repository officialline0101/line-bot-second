from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

# ここにLINEからもらった秘密のキーを貼るよ💕
LINE_CHANNEL_ACCESS_TOKEN = os.environ["0YU5gWvZd3IlR/XO2S8L2U6LL/vPwQr6zV2pGoVFaYFOnhZcDx7WoxnAcR7G58j2TBj+FTYOTlI7bmDiQ39/8jhs4xDdnQSHqqmI9eG0RWE4Q7i/g8G/JdRFEPoxUYMXUq3nxrpRYdKxAyWPH+93lgdB04t89/1O/w1cDnyilFU="]
LINE_CHANNEL_SECRET = os.environ["7f44df3f356e512ffb046676e56f46f0"]

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    reply_text = "やっほ〜！メッセージありがとう💖"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run()
