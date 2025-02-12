from datetime import datetime, timedelta, date
import requests
import json
import os

if __name__ == '__main__':
    content = ""

    # 获取今天的日期
    today = datetime.today().date()
    # print("起始日期:", today)
    content += "起始日期: {}\n".format(today)

    # 计算七天后的日期
    seven_days_later = today + timedelta(days=7)
    # print("终止日期:", seven_days_later)
    content += "终止日期: {}\n".format(seven_days_later)

    # print('\r开始查询场地')
    link = 'https://api.sport.sheffield.ac.uk/api/site/HO/activitygroup/BAD/activity/BADTN/slots'
    # link = 'https://api.sport.sheffield.ac.uk/api/site/HO/activitygroup/GSC-MUGA/activity/GSC-SMUGA-TEN/slots'
    url = '{}?plus2Id=0&start={}T00%3A00%3A00.000Z&end={}T00%3A00%3A00.000Z&groupResources=true'.format(link, today, seven_days_later)
    # print(url)
    courts = requests.get(url).text
    courts = courts.replace('false', 'False')
    courts = courts.replace('true', 'True')
    courts = eval(courts)

    content += "正在查询晚上7点之后的场次\n"

    time_threshold = 19
    filted_courts = []
    for court in courts:
        filted = False
        if int(court['start'].split('T')[1].split(':')[0]) < time_threshold: filted = True
        if court['available'] == 0: filted = True
        if not filted:
            filted_courts.append(court)

    weekday_dict = ['Mon', 'Tue', 'Wen', 'Thu', 'Fri', 'Sat', 'Sun']

    # print('\r查询结果:')
    content += "查询结果:"
    if len(filted_courts)>0:

        current = None
        for court in filted_courts:
            if court['start'].split('T')[0] != current:
                current = court['start'].split('T')[0]
                # print('\n'+current, weekday_dict[date(int(current.split('-')[0]), int(current.split('-')[1]), int(current.split('-')[2])).weekday()])
                content += "\n{} {}\n".format(
                    current,
                    weekday_dict[date(int(current.split('-')[0]), int(current.split('-')[1]), int(current.split('-')[2])).weekday()]
                ) 
            # print(' {}    available: {}'.format(court['start'].split('T')[1], str(court['available'])))
            content += ' {}    available: {}\n'.format(
                court['start'].split('T')[1], 
                str(court['available'])
            )
        content += '\n 来个HXD自觉一点定个场子'
    else:
        content += '\n\n 这周也没有场子啊🅰\n'
        content += ' 叫我来干啥\n'
        content += ' hei不如去攀岩'

    # print()
    # print(content)

    bot_key = os.getenv("BOT_API_KEY")

    url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}".format(bot_key.replace('_','-'))

    data = {
        "msgtype": "text",
        "text": {
            "content": content,
        }
    }

    res = requests.post(url=url,data=json.dumps(data))
    print(res.text)
