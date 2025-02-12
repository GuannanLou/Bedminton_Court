from datetime import datetime, timedelta
import requests
import argparse

# 解析命令行参数
parser = argparse.ArgumentParser(
    description='查询谢菲尔德大学羽毛球场地预定信息',
    formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument('--day_offset', '-d', help='日期偏移量 (例如: 1 表示明天)', default=0)
parser.add_argument('--threshold',  '-t', help='时间阈值 (例如: 18 表示筛选晚上6点后的场地)', default=18)
args = parser.parse_args()

if __name__ == '__main__':
    # 获取今天的日期，并根据偏移量计算起始日期
    today = datetime.today().date()
    start_date = today + timedelta(days=int(args.day_offset))
    print("起始日期:", start_date)

    # 计算七天后的终止日期
    end_date = start_date + timedelta(days=7)
    print("终止日期:", end_date)

    # 开始请求场地数据
    print('开始查询场地...')
    link = 'https://api.sport.sheffield.ac.uk/api/site/HO/activitygroup/BAD/activity/BADTN/slots'
    # 构建 API 请求 URL
    url = '{}?plus2Id=0&start={}T00%3A00%3A00.000Z&end={}T00%3A00%3A00.000Z&groupResources=true'.format(
        link, start_date, end_date
    )
    # 获取 API 数据
    courts = requests.get(url).text
    # 将布尔值转换为 Python 格式
    courts = courts.replace('false', 'False').replace('true', 'True')
    courts = eval(courts)

    # 筛选条件设置
    print('\n查询结果:')
    time_threshold = int(args.threshold)
    filted_courts = []
    for court in courts:
        # 筛选条件: 场地开始时间在时间阈值之后，且有空余位置
        filted = False
        if int(court['start'].split('T')[1].split(':')[0]) < time_threshold:
            filted = True
        if court['available'] == 0:
            filted = True
        if not filted:
            filted_courts.append(court)

    # 按日期分组打印结果
    current_date = None
    for court in filted_courts:
        court_date = court['start'].split('T')[0]  # 提取日期
        court_time = court['start'].split('T')[1]  # 提取时间
        if court_date != current_date:
            current_date = court_date
            print(current_date)  # 输出新的日期
        print('\t{}    available: {}'.format(court_time, court['available']))