# 青龙面板可用的脚本
import os
import json
import hmac
import time
import base64
import hashlib
import requests
import urllib.parse
from datetime import datetime, timedelta


if "DD_BOT_TOKEN" in os.environ and os.environ["DD_BOT_TOKEN"] and "DD_BOT_SECRET" in os.environ and os.environ["DD_BOT_SECRET"]:
    DD_BOT_TOKEN = os.environ["DD_BOT_TOKEN"]
    DD_BOT_SECRET = os.environ["DD_BOT_SECRET"]

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
    msg = '#### 美元/人民币汇率\n\n' \
            '# <red>'+records[0]['values'][0] + '</red>\n\n'\
            '###### '+records[0]['date']+'更新[详情](http://www.chinamoney.com.cn/chinese/bkccpr/)'
    title='美元/人民币汇率中间价公告'
    dingding_bot(title,msg)


def dingding_bot(title, content):
    timestamp = str(round(time.time() * 1000))  # 时间戳
    secret_enc = DD_BOT_SECRET.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, DD_BOT_SECRET)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))  # 签名
    print('开始使用 钉钉机器人 推送消息...', end='')
    url = f'https://oapi.dingtalk.com/robot/send?access_token={DD_BOT_TOKEN}&timestamp={timestamp}&sign={sign}'
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    data = {
        'msgtype': 'markdown',
        'markdown': {
            "title":f'{title}',
            'text': f'{content}'
        }
    }
    response = requests.post(url=url, data=json.dumps(data), headers=headers, timeout=15).json()
    if not response['errcode']:
        print('推送成功！')
    else:
        print('推送失败！')

        
def main():
    records = query_records()
    send_msg(records) 

    
if __name__ == '__main__':
    main()           
