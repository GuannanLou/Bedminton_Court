from datetime import datetime, timedelta, date
import requests
import json
import hashlib
import base64
import os
import random
import time


def get_img(img_path):
    with open(img_path, 'rb') as f:
        im_bytes = f.read()
        im_b64 = str(base64.b64encode(im_bytes), "utf-8")
    with open(img_path, 'rb') as f:
        im_fd = f.read()
        md = hashlib.md5()
        md.update(im_fd)
        im_md5 = md.hexdigest()
    return im_b64, im_md5


def get_court(content, today):
    content = ""
    content += "\n\n正在查询晚上7点之后的场次\n"
    # 获取今天的日期
    content += "起始日期: {}\n".format(today)
    # 计算七天后的日期
    seven_days_later = today + timedelta(days=6)
    content += "终止日期: {}\n".format(seven_days_later)

    link = 'https://api.sport.sheffield.ac.uk/api/site/HO/activitygroup/BAD/activity/BADTN/slots'
    # link = 'https://api.sport.sheffield.ac.uk/api/site/HO/activitygroup/GSC-MUGA/activity/GSC-SMUGA-TEN/slots'
    url = '{}?plus2Id=0&start={}T00%3A00%3A00.000Z&end={}T00%3A00%3A00.000Z&groupResources=true'.format(link, today,
                                                                                                        seven_days_later)
    courts = requests.get(url).text
    courts = courts.replace('false', 'False')
    courts = courts.replace('true', 'True')
    courts = eval(courts)

    weekday_dict = ['Mon', 'Tue', 'Wen', 'Thu', 'Fri', 'Sat', 'Sun']

    time_threshold = 19
    filtered_courts = []
    for court in courts:
        filtered = False
        current = court['start'].split('T')[0]
        weekday = weekday_dict[
            date(int(current.split('-')[0]), int(current.split('-')[1]), int(current.split('-')[2])).weekday()]
        if int(court['start'].split('T')[1].split(':')[0]) < time_threshold: filted = True
        if weekday in ['Sat', 'Sun']: filted = False
        if court['available'] == 0: filted = True
        if not filtered:
            filtered_courts.append(court)
    return content, filtered_courts


# def custom_api():
#     url_dog = "https://api.oick.cn/api/dog"
#     res = requests.get(url_dog)
#     return json.loads(res.text)


def get_court_text(today):
    content, filtered_courts = get_court("", today)
    weekday_dict = ['Mon', 'Tue', 'Wen', 'Thu', 'Fri', 'Sat', 'Sun']
    # custom_api_res = custom_api()

    content += "查询结果:\n"
    if len(filtered_courts) > 0:
        current = None
        for court in filtered_courts:
            if court['start'].split('T')[0] != current:
                current = court['start'].split('T')[0]
                content += "\n{} {}\n".format(
                    current,
                    weekday_dict[date(int(current.split('-')[0]), int(current.split('-')[1]),
                                      int(current.split('-')[2])).weekday()]
                )
            content += ' {}    available: {}\n'.format(
                court['start'].split('T')[1],
                str(court['available'])
            )
        state = True
    else:
        content += '\n 这周无场子\n'
        content += ' 南哥真帅\n'
        content += '\n'

        state = False

    stat_text = '没场，不用订' if not state else random.choice([
        '老黑自觉定场',
        '顾顾自觉定场',
        '学弟自觉定场',
        '学姐自觉定场',
    ])
    content += '\n'
    content += stat_text
    content += '\n\n警世格言：\n'
    # content += custom_api_res
    content = stat_text + content + '\n'
    return content


def send_text(url, content):
    msg = {
        "msgtype": "text",
        "text": {
            "content": content,
            # "mentioned_list": ["lilikili4050"],
            "mentioned_mobile_list": ["15070919071"]
        }
    }
    res_text = requests.post(url=url, data=json.dumps(msg))
    return res_text


def send_img(url, image):
    im_b64, im_md5 = get_img(image)
    headers = {"content-type": "application/json"}
    msg = {"msgtype": "image", "image": {"base64": im_b64, "md5": im_md5}}
    res_image = requests.post(url=url, headers=headers, json=msg)
    return res_image


def send_card(url):
    msg = {
        "msgtype": "template_card",
        "template_card": {
            "card_type": "text_notice",
            "source": {
                "icon_url": "https://wework.qpic.cn/wwpic/252813_jOfDHtcISzuodLa_1629280209/0",
                "desc": "企业微信",
                "desc_color": 0
            },
            "main_title": {
                "title": "欢迎使用企业微信",
                "desc": "您的好友正在邀请您加入企业微信"
            },
            "emphasis_content": {
                "title": "100",
                "desc": "数据含义"
            },
            "quote_area": {
                "type": 1,
                "url": "https://work.weixin.qq.com/?from=openApi",
                "appid": "APPID",
                "pagepath": "PAGEPATH",
                "title": "引用文本标题",
                "quote_text": "Jack：企业微信真的很好用~\nBalian：超级好的一款软件！"
            },
            "sub_title_text": "下载企业微信还能抢红包！",
            "horizontal_content_list": [
                {
                    "keyname": "邀请人",
                    "value": "张三"
                },
                {
                    "keyname": "企微官网",
                    "value": "点击访问",
                    "type": 1,
                    "url": "https://work.weixin.qq.com/?from=openApi"
                },
                {
                    "keyname": "企微下载",
                    "value": "企业微信.apk",
                    "type": 2,
                    "media_id": "MEDIAID"
                }
            ],
            "jump_list": [
                {
                    "type": 1,
                    "url": "https://work.weixin.qq.com/?from=openApi",
                    "title": "企业微信官网"
                },
                {
                    "type": 2,
                    "appid": "APPID",
                    "pagepath": "PAGEPATH",
                    "title": "跳转小程序"
                }
            ],
            "card_action": {
                "type": 1,
                "url": "https://work.weixin.qq.com/?from=openApi",
                "appid": "APPID",
                "pagepath": "PAGEPATH"
            }
        }
    }
    res_text = requests.post(url=url, data=json.dumps(msg))
    return res_text


if __name__ == '__main__':
    bot_key = os.getenv("BOT_API_KEY")
    url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}".format(bot_key.replace('_', '-'))

    today = datetime.today().date()
    content = get_court_text(today)

    image = './res/profile.png'

    send_img(url, image)
    send_text(url, content)
    # send_card(url)
