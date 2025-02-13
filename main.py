from datetime import datetime, timedelta, date
import requests
import json
import base64
import os

if __name__ == '__main__':
    content = ""
    content += "正在查询晚上7点之后的场次\n"

    # 获取今天的日期
    today = datetime.today().date()
    # print("起始日期:", today)
    content += "起始日期: {}\n".format(today)

    # 计算七天后的日期
    seven_days_later = today + timedelta(days=6)
    # print("终止日期:", seven_days_later)
    content += "终止日期: {}\n".format(seven_days_later)

    # print('\r开始查询场地')
    link = 'https://api.sport.sheffield.ac.uk/api/site/HO/activitygroup/BAD/activity/BADTN/slots'
    # link = 'https://api.sport.sheffield.ac.uk/api/site/HO/activitygroup/GSC-MUGA/activity/GSC-SMUGA-TEN/slots'
    url = '{}?plus2Id=0&start={}T00%3A00%3A00.000Z&end={}T00%3A00%3A00.000Z&groupResources=true'.format(link, today,
                                                                                                        seven_days_later)
    # print(url)
    courts = requests.get(url).text
    courts = courts.replace('false', 'False')
    courts = courts.replace('true', 'True')
    courts = eval(courts)

    time_threshold = 19
    filted_courts = []
    for court in courts:
        filted = False
        if int(court['start'].split('T')[1].split(':')[0]) < time_threshold: filted = True
        if court['available'] == 0: filted = True
        if not filted:
            filted_courts.append(court)

    weekday_dict = ['Mon', 'Tue', 'Wen', 'Thu', 'Fri', 'Sat', 'Sun']

    # image base64 and md5
    # image = 'https://github.com/GuannanLou/Bedminton_Court/res/profile.png'
    # image = 'https://raw.githubusercontent.com/GuannanLou/Bedminton_Court/refs/heads/master/res/profile.png'
    image = './res/profile.png'
    with open(image, 'rb') as f:
        im_bytes = f.read()
        im_b64 = str(base64.b64encode(im_bytes), "utf-8")
    with open(image, 'rb') as f:
        im_fd = f.read()
        md = hashlib.md5()
        md.update(im_b64)
        im_md5 = md.hexdigest()

    # print('\r查询结果:')
    content += "查询结果:"
    if len(filted_courts) > 0:
        current = None
        for court in filted_courts:
            if court['start'].split('T')[0] != current:
                current = court['start'].split('T')[0]
                # print('\n'+current, weekday_dict[date(int(current.split('-')[0]), int(current.split('-')[1]), int(current.split('-')[2])).weekday()])
                content += "\n{} {}\n".format(
                    current,
                    weekday_dict[date(int(current.split('-')[0]), int(current.split('-')[1]),
                                      int(current.split('-')[2])).weekday()]
                )
                # print(' {}    available: {}'.format(court['start'].split('T')[1], str(court['available'])))
            content += ' {}    available: {}\n'.format(
                court['start'].split('T')[1],
                str(court['available'])
            )
        content += '\n 黑奴自觉定场'
    else:
        content += '\n\n 这周也没有场子啊🅰\n'
        content += ' 叫我来干啥\n'
        content += ' hei不如去攀岩'

    # print()
    # print(content)

    bot_key = os.getenv("BOT_API_KEY")

    # send text
    url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}".format(bot_key.replace('_', '-'))
    data = {
        "msgtype": "text",
        "text": {
            "content": content,
        }
    }
    res_text = requests.post(url=url, data=json.dumps(data))
    # print(res.text)
    # send image
    headers = {"content-type": "application/json"}
    msg = {"msgtype": "image", "image": {"base64": im_b64, "md5": im_md5}}
    res_image = requests.post(url=url, headers=headers, json=msg)
