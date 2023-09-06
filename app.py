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

from lunar_python import Lunar, EightChar
from datetime import datetime
from lunar_python.util import LunarUtil
from prettytable import PrettyTable


app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

def calculate_bazi(year, month, day, hour=0):
    #  datetime 对象
    # date_obj = datetime.strptime(date_str, '%Y-%m-%d %H')
    date_obj = datetime(year, month, day, hour)
    lunar = Lunar.fromDate(date_obj)

    # 使用者輸入的流派
    # sect = inst(input("請輸入流派（1代表流派1，2代表流派2）："))
    sect='2'
    # 設置流派
    eight_char = EightChar.fromLunar(lunar)
    eight_char.setSect(sect)

    # 新的流派
    new_sect = eight_char.getSect()
    # print("新的流派:", new_sect)

    # 八字訊息
    eight_char_info = lunar.getEightChar()
    print(f"八字：{eight_char_info}")

    #
    # 获取年支十神
    year_shi_shen_zhi = eight_char.getYearShiShenZhi()
    print(f'年支十神 = {year_shi_shen_zhi}')

    # 获取月支十神
    month_shi_shen_zhi = eight_char.getMonthShiShenZhi()
    print(f'月支十神 = {month_shi_shen_zhi}')

    # 获取日支十神
    day_shi_shen_zhi = eight_char.getDayShiShenZhi()
    print(f'日支十神 = {day_shi_shen_zhi}')

    # 获取时支十神
    time_shi_shen_zhi = eight_char.getTimeShiShenZhi()
    print(f'时支十神 = {time_shi_shen_zhi}')


    # 获取年、月、日、时的天干十神
    year_shi_shen_gan = eight_char.getYearShiShenGan()
    month_shi_shen_gan = eight_char.getMonthShiShenGan()
    day_shi_shen_gan = eight_char.getDayShiShenGan()
    time_shi_shen_gan = eight_char.getTimeShiShenGan()

    # 打印结果
    print(f'年的天干十神为：{year_shi_shen_gan}')
    print(f'月的天干十神为：{month_shi_shen_gan}')
    print(f'日的天干十神为：{day_shi_shen_gan}')
    print(f'时的天干十神为：{time_shi_shen_gan}')

    result=dayouten('辛','丁')
    print(result)

    #大運
    # 获取男运
    gender = 1
    yun = eight_char.getYun(gender)

    # 起运
    start_year = yun.getStartYear()
    start_month = yun.getStartMonth()
    start_day = yun.getStartDay()
    print(f'出生{start_year}年{start_month}个月{start_day}天后起运')

    daydan=eight_char.getDayGan()
    # print(daydan)

    # 获取大运表
    daYunArr = yun.getDaYun()
    for i, daYun in enumerate(daYunArr):
        start_year = daYun.getStartYear()
        start_age = daYun.getStartAge()
        gan_zhi = daYun.getGanZhi()

        if i<1:
            
            print(f'大运[{i}] = {start_year}年 {start_age}岁 {gan_zhi} ')
        else:
            first_char = gan_zhi[0]
            minded=dayouten(daydan,first_char)
            print(f'大运[{i}] = {start_year}年 {start_age}岁 {gan_zhi}  {minded} ')


    # str_eight_char_info=str(eight_char_info)
    # print(str_eight_char_info[3:5])
    # table = PrettyTable(["46-120", "31-45","16-30", "1-15"])
    # table.add_row(["時", "日","月", "年"])
    # table.add_row([time_shi_shen_gan, day_shi_shen_gan,month_shi_shen_gan, year_shi_shen_gan])

    # table.add_row([str_eight_char_info[9:10], str_eight_char_info[6:7],str_eight_char_info[3:4],str_eight_char_info[0:1]])
    # table.add_row([str_eight_char_info[10:11], str_eight_char_info[7:8],str_eight_char_info[4:5],str_eight_char_info[1:2]])
    # table.add_row([time_shi_shen_zhi, day_shi_shen_zhi,month_shi_shen_zhi, year_shi_shen_zhi])
    # print(table)
    return str_eight_char_info

    # return f"{year_stem}{year_branch}年 {month_stem}{month_branch}月 {day_stem}{day_branch}日 {hour_stem}{hour_branch}時"

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
            # Check if the hour is included
            if len(msg.split()) == 2:
                dt = datetime.strptime(msg, '%Y-%m-%d %H')
                reply_msg = calculate_bazi(dt.year, dt.month, dt.day, dt.hour)
            else:
                dt = datetime.strptime(msg, '%Y-%m-%d')
                reply_msg = calculate_bazi(dt.year, dt.month, dt.day)
        except:
            reply_msg = "日期格式不正確。請重新輸入您的出生年月日 (格式: YYYY-MM-DD)，若知道出生時間也可加入 (格式: YYYY-MM-DD HH)。"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_msg))

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
