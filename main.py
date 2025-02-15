from datetime import datetime, timedelta, date
import requests
import json
import hashlib
import base64
import os
import random

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
    content += "正在查询晚上7点之后的场次\n"

    # 获取今天的日期
    content += "起始日期: {}\n".format(today)

    # 计算七天后的日期
    seven_days_later = today + timedelta(days=6)
    content += "终止日期: {}\n".format(seven_days_later)

    link = 'https://api.sport.sheffield.ac.uk/api/site/HO/activitygroup/BAD/activity/BADTN/slots'
    # link = 'https://api.sport.sheffield.ac.uk/api/site/HO/activitygroup/GSC-MUGA/activity/GSC-SMUGA-TEN/slots'
    url = '{}?plus2Id=0&start={}T00%3A00%3A00.000Z&end={}T00%3A00%3A00.000Z&groupResources=true'.format(link, today, seven_days_later)
    print(url)
    
    courts = requests.get(url).text
    courts = courts.replace('false', 'False')
    courts = courts.replace('true', 'True')
    courts = eval(courts)

    weekday_dict = ['Mon', 'Tue', 'Wen', 'Thu', 'Fri', 'Sat', 'Sun']
    
    time_threshold = 19
    filted_courts = []
    for court in courts:
        filted = False
        if int(court['start'].split('T')[1].split(':')[0]) < time_threshold: filted = True
        if court['available'] == 0: filted = True
        current = court['start'].split('T')[0]
        weekday = weekday_dict[date(int(current.split('-')[0]), int(current.split('-')[1]), int(current.split('-')[2])).weekday()]
        if weekday in ['Sat', 'Sun']: filted = False
        if not filted:
            filted_courts.append(court)
    return content, filted_courts

def get_court_text(today):
    content, filted_courts = get_court("", today)
    
    weekday_dict = ['Mon', 'Tue', 'Wen', 'Thu', 'Fri', 'Sat', 'Sun']

    content += "查询结果:"
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
            content += ' {}    available: {}\n'.format(
                court['start'].split('T')[1],
                str(court['available'])
            )
        content += random.choice([
            '\n 老黑自觉定场',
            '\n 顾顾自觉定场',
            '\n 学弟自觉定场',
            '\n 学姐自觉定场',
        ])
    else:
        content += '\n\n 这周也没有场子啊🅰\n'
        content += ' 叫我来干啥\n'
        content += ' hei不如去攀岩'

    return content

def send_text(url, content):
    msg = {"msgtype": "text", "text": {"content": content}}
    res_text = requests.post(url=url, data=json.dumps(msg))
    return res_text

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

    image = './res/profile.png'

    send_text(url, content)
    send_img(url, image)
