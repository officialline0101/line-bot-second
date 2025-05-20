from flask import Flask, request, abort
from linebot.v3.webhook import WebhookHandler
from linebot.v3.messaging import MessagingApi, Configuration, ApiClient
from linebot.v3.messaging.models import ReplyMessageRequest, TextMessage, FlexMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.exceptions import InvalidSignatureError

import os
import json
from dotenv import load_dotenv
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# .env 読み込み
load_dotenv()
ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")  # スプレッドシートIDを環境変数から取得

# Flask 初期化
app = Flask(__name__)

# LINE API設定
configuration = Configuration(access_token=ACCESS_TOKEN)
api_client = ApiClient(configuration=configuration)
line_bot_api = MessagingApi(api_client)
handler = WebhookHandler(CHANNEL_SECRET)

# GoogleスプレッドシートからFlex JSONを取得
def get_flex_json_from_sheet(keyword):
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
        client = gspread.authorize(creds)

        sheet = client.open_by_key(SPREADSHEET_ID).sheet1  # シート1を対象
        records = sheet.get_all_records()

        for row in records:
            if row['キーワード'] == keyword:
                return json.loads(row['JSON（Flexメッセージの中身）'])  # 文字列 → dict変換
    except Exception as e:
        print("❌ スプレッドシート読み込みエラー:", e)
    return None

# Webhookのエンドポイント
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

# メッセージ受信処理
@handler.add(MessageEvent)
def handle_message(event):
    if isinstance(event.message, TextMessageContent):
        user_message = event.message.text.strip()

        flex_data = get_flex_json_from_sheet(user_message)
        if flex_data:
            # Flexメッセージで返信
            response = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    FlexMessage(
                        alt_text="Flexメッセージの返信です",
                        contents=flex_data
                    )
                ]
            )
        else:
            # 該当キーワードがないときはテキストで返す
            response = ReplyMessageRequest(
                reply_token=event.reply_token,
                messages=[
                    TextMessage(text=f"『{user_message}』に対応するメッセージが見つかりませんでした。")
                ]
            )

        line_bot_api.reply_message(response)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))  # Renderが自動でセットしてくれるPORTを使う！
    app.run(host="0.0.0.0", port=port)
