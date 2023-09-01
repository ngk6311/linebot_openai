from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *
from datetime import datetime
import os
from linebot.models import FlexSendMessage


app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

def calculate_bazi(year, month, day, hour=0):
    Heavenly_Stems = '甲乙丙丁戊己庚辛壬癸'
    Earthly_Branches = '子丑寅卯辰巳午未申酉戌亥'
    
    year_stem = Heavenly_Stems[(year - 4) % 10]
    year_branch = Earthly_Branches[(year - 4) % 12]
    month_stem = Heavenly_Stems[(year * 12 + month - 3) % 10]
    month_branch = Earthly_Branches[month % 12]
    day_stem = Heavenly_Stems[(year * month * day) % 10]
    day_branch = Earthly_Branches[day % 12]
    hour_stem = Heavenly_Stems[(year * month * day + hour) % 10]
    hour_branch = Earthly_Branches[hour % 12]

    return f"{year_stem}{year_branch}年 {month_stem}{month_branch}月 {day_stem}{day_branch}日 {hour_stem}{hour_branch}時"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    msg = event.message.text
    if "出生" in msg:
        reply_msg = "請輸入您的出生年月日 (格式: YYYY-MM-DD)，若知道出生時間也可加入 (格式: YYYY-MM-DD HH)。"
    else:
        try:
            # ... (略過原本的程式碼)
            
            # 建立表格格式的彈性訊息
            bazi_info = calculate_bazi(dt.year, dt.month, dt.day, dt.hour)
            reply_msg = {
                "type": "bubble",
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": "八字資訊", "weight": "bold", "size": "xl"},
                        {"type": "text", "text": bazi_info, "margin": "lg", "wrap": True}
                    ]
                }
            }
        except:
            reply_msg = "日期格式不正確。請重新輸入您的出生年月日 (格式: YYYY-MM-DD)，若知道出生時間也可加入 (格式: YYYY-MM-DD HH)。"

    flex_message = FlexSendMessage(alt_text="八字資訊", contents=reply_msg)
    line_bot_api.reply_message(event.reply_token, flex_message)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
