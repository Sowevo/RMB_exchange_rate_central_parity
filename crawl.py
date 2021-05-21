import json

import requests
import argparse
from dingtalkchatbot.chatbot import DingtalkChatbot
from datetime import datetime, timedelta

url = "http://www.chinamoney.com.cn/ags/ms/cm-u-bk-ccpr/CcprHisNew"

def date_add(time, days):
    """时间加上一定的天,可以是负数"""
    return time + timedelta(days)


def query_records():
    now = datetime.now()
    end_time = date_add(now, -60)
    data = {
        'startDate': end_time.strftime("%Y-%m-%d"),
        'endDate': now.strftime("%Y-%m-%d"),
        'currency': 'USD/CNY',
        'pageNum': '1',
        'pageSize': '1'
    }

    response = requests.request("POST", url, params=data)

    result = json.loads(response.text)
    return result['records']


def send_msg(records):
    if FLAGS.secret is not None and FLAGS.access_token is not None:
        webhook = 'https://oapi.dingtalk.com/robot/send?access_token={}'.format(FLAGS.access_token)
        secret = FLAGS.secret
        bot = DingtalkChatbot(webhook, secret=secret)
        msg = '#### 美元/人民币汇率\n\n' \
              '# <red>'+records[0]['values'][0] + '</red>\n\n'\
              '###### '+records[0]['date']+'更新[详情](http://www.chinamoney.com.cn/chinese/bkccpr/)'
        bot.send_markdown(
            title='美元/人民币汇率中间价公告',
            text=msg
        )


def main():
    records = query_records()
    send_msg(records)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='从中国人民银行网站抓取货币政策司的人民币汇率中间价公告')
    parser.add_argument('--access_token', type=str, help='发送钉钉消息的参数,access_token,不填不发钉钉消息')
    parser.add_argument('--secret', type=str, help='发送钉钉消息的参数,secret,不填不发钉钉消息')
    FLAGS = parser.parse_args()
    main()