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


def get_court(today):
    # content = ""
    # content += "\n\n正在查询晚上7点之后的场次\n"
    content = {}

    # 获取今天的日期
    # content += "起始日期: {}\n".format(today)
    content["start_date"] = "{}".format(today)

    # 计算七天后的日期
    seven_days_later = today + timedelta(days=6)
    # content += "终止日期: {}\n".format(seven_days_later)
    content["end_date"] = "{}".format(seven_days_later)

    link = 'https://api.sport.sheffield.ac.uk/api/site/HO/activitygroup/BAD/activity/BADTN/slots'
    # link = 'https://api.sport.sheffield.ac.uk/api/site/HO/activitygroup/GSC-MUGA/activity/GSC-SMUGA-TEN/slots'
    url = '{}?plus2Id=0&start={}T00%3A00%3A00.000Z&end={}T00%3A00%3A00.000Z&groupResources=true'.format(link, today,
                                                                                                        seven_days_later)
    # print(url)

    courts = requests.get(url).text
    courts = courts.replace('false', 'False')
    courts = courts.replace('true', 'True')
    courts = eval(courts)

    weekday_dict = ['Mon', 'Tue', 'Wen', 'Thu', 'Fri', 'Sat', 'Sun']

    time_threshold = 19
    filted_courts = []
    for court in courts:
        filted = False
        current = court['start'].split('T')[0]
        weekday = weekday_dict[
            date(int(current.split('-')[0]), int(current.split('-')[1]), int(current.split('-')[2])).weekday()]
        if int(court['start'].split('T')[1].split(':')[0]) < time_threshold: filted = True
        if weekday in ['Sat', 'Sun']: filted = False
        if court['available'] == 0: filted = True
        if not filted:
            filted_courts.append(court)
    return content, filted_courts


def custom_api():
    url_dog = "https://api.oick.cn/api/dog"
    res = requests.get(url_dog)
    return json.loads(res.text)


def get_court_text(today):
    content, filted_courts = get_court(today)

    weekday_dict = ['Mon', 'Tue', 'Wen', 'Thu', 'Fri', 'Sat', 'Sun']

    custom_api_res = custom_api()

    # state = False

    # content += "查询结果:\n"
    if len(filted_courts) > 0:
        current = None
        for court in filted_courts:
            if court['start'].split('T')[0] != current:
                current = court['start'].split('T')[0]
                content += "\n{} {}\n".format(
                    current,
                    weekday_dict[date(int(current.split('-')[0]), int(current.split('-')[1]),
                                      int(current.split('-')[2])).weekday()]
                )
            # content += ' {}    available: {}\n'.format(
            #     court['start'].split('T')[1],
            #     str(court['available'])
            # )
            content["booking_detail"] = ' {}    available: {}\n'.format(
                court['start'].split('T')[1],
                str(court['available'])
            )
        state = True
    else:
        # content += '\n 这周也没有场子啊🅰\n'
        # content += ' 叫我来干啥\n'
        # content += ' hei不如去攀岩'
        # content += '\n'
        content["booking_detail"] = '这周也没有场子啊🅰\n hei不如去攀岩'

        state = False

    content["booking_info"] = '没场，不用订' if not state else random.choice([
        '老黑自觉定场',
        '顾顾自觉定场',
        '学弟自觉定场',
        '学姐自觉定场',
    ])

    content["warning"] = custom_api_res

    # content += '\n'
    # content += stat_text

    # content += '\n\n警世格言：\n'
    # content += custom_api_res

    # content = stat_text + content + '\n'

    return content


def send_text(url, content):
    msg = {
        "msgtype": "text",
        "text": {
            "content": content,
            # "mentioned_list": ["lilikili4050"],
            # "mentioned_mobile_list": ["15070919071"]
        }
    }
    res_text = requests.post(url=url, data=json.dumps(msg))
    return res_text


def send_card(url, content):
    msg = {
        "msgtype": "template_card",
        "template_card": {
            "card_type": "text_notice",
            "main_title": {
                "title": "羽毛球场次查询",
                "desc": "您好，我是您的羽毛球场次查询小黑奴"
            },
            "sub_title_text": "正在查询晚上7点之后的场次",
            "horizontal_content_list": [
                {
                    "keyname": "起始日期",
                    "value": content["start_date"]
                },
                {
                    "keyname": "终止日期",
                    "value": content["end_date"]
                },
            ],
            "emphasis_content": {
                "title": content["booking_info"],
                "desc": "点击卡片进入订场页面"
            },
            "jump_list": [
                {
                    "type": 1,
                    "url": "https://api.oick.cn/api/dog",
                    "title": "警世格言"
                },
                {
                    "type": 1,
                    "url": "https://raw.githubusercontent.com/GuannanLou/Bedminton_Court/refs/heads/master/res/profile.png",
                    "title": "每日猫图"
                }
            ],
            "card_action": {
                "type": 1,
                "url": "https://sport.sheffield.ac.uk/activities/0/HO/BAD/BADTN",
            }
        }
    }
    headers = {"content-type": "application/json"}
    res_card = requests.post(url=url, data=json.dumps(msg))
    return res_card


def send_img(url, image):
    im_b64, im_md5 = get_img(image)

    headers = {"content-type": "application/json"}
    msg = {"msgtype": "image", "image": {"base64": im_b64, "md5": im_md5}}
    res_image = requests.post(url=url, headers=headers, json=msg)
    return res_image


if __name__ == '__main__':
    bot_key = os.getenv("BOT_API_KEY")
    url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}".format(bot_key.replace('_', '-'))

    today = datetime.today().date()
    content = get_court_text(today)
    send_card(url, content)

    # image = './res/profile.png'

    # send_img(url, image)
    # send_text(url, content)
    # send_card(url)
