#!/usr/local/bin/python3.9
#coding:utf-8

import logging
from dingtalkchatbot.chatbot import DingtalkChatbot
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)-15s [%(filename)s:%(lineno)d] %(levelname)s %(message)s'
)
import bs4
import time
import argparse
import re
from pbc_http import get_url_content
from pbc_conf import HOME_PAGE, LIST_PAGE_URL_PATTERN

chinese_pattern = re.compile("[\u4e00-\u9fa5]")
number_pattern = re.compile("[0-9.]")


class ExchangeRate(object):
    """汇率"""

    def __init__(self, source, source_num, target, target_num):
        self.source = source
        self.source_num = source_num
        self.target = target
        self.target_num = target_num


class News(object):
    """公告对象"""

    def __init__(self, title, url, content=None, news_time=None, exchange_rate_list=None):
        self.title = title
        self.url = url
        self.content = content
        self.news_time = news_time
        self.exchange_rate_list = exchange_rate_list

    def __str__(self) -> str:
        msg = '标题:' + self.title + '\n' \
               + '时间:' + self.news_time + '\n' \
               + '汇率:' + '\n'
        for exchange_rate in self.exchange_rate_list:
            msg = msg + '\t'+ exchange_rate.source_num + exchange_rate.source + '=' \
                  + exchange_rate.target_num + exchange_rate.target + '\n'
        return msg



def extract_chinese(txt):
    """提取中文"""
    return "".join(chinese_pattern.findall(txt))


def extract_number(txt):
    """提取数字"""
    return "".join(number_pattern.findall(txt))


def extract_news_url(text):
    """ 从目录页抽取公告链接 """
    soup = bs4.BeautifulSoup(text, 'html.parser')
    url_list = []
    for item in soup.select('font[class="newslist_style"] a'):
        news_url = HOME_PAGE + item.get_attribute_list('href')[0]
        url_list.append(News(title=item.text, url=news_url))
    return url_list


def extract_news_content(text, item):
    """从公告页抽取公告内容 """
    soup = bs4.BeautifulSoup(text, 'html.parser')
    content = soup.select_one('#zoom > p:nth-child(1)').text
    news_time = soup.select_one('#shijian').text
    item.news_time = news_time
    item.content = content


def analyze_news_content(item):
    """分析公告内容 """
    exchange_rate_list = []
    for info in item.content.replace("。", "").replace("，", ",").split("：")[1].split(","):
        split = info.strip().split("对")
        exchange_rate_list.append(ExchangeRate(
            extract_chinese(split[0]),
            extract_number(split[0]),
            extract_chinese(split[1]),
            extract_number(split[1])
        ))
    item.exchange_rate_list = exchange_rate_list


def send_news_content(item):
    """发送公告内容 """
    if FLAGS.secret is not None and FLAGS.access_token is not None:
        webhook = 'https://oapi.dingtalk.com/robot/send?access_token={}'.format(FLAGS.access_token)
        secret = FLAGS.secret
        bot = DingtalkChatbot(webhook, secret=secret)
        msg_temple = '# 人民币汇率中间价公告\n\n' \
                     '{}' \
                     '###### {}发布 [点击查看]({})'
        exchange_rate_str = ''
        for exchange_rate in item.exchange_rate_list:
            exchange_rate_str = exchange_rate_str + "" + exchange_rate.source_num + exchange_rate.source + '=' \
                  + exchange_rate.target_num + exchange_rate.target + '\n\n'
        msg = msg_temple.format(exchange_rate_str, item.news_time, item.url)
        bot.send_markdown(
            title=item.title,
            text=msg
        )


def main():
    # 如果只抓取最新的一条,只取第一页
    if FLAGS.single == 1:
        FLAGS.num_pages = 1
    news_link_list = []
    # 抽取所有的公告链接
    for page_no in range(1, FLAGS.num_pages + 1):
        list_page_url = LIST_PAGE_URL_PATTERN.format(page_no)
        logging.info('Parsing list page@[%d] ...', page_no)
        text = get_url_content(list_page_url)
        extracted = extract_news_url(text)
        news_link_list.extend(extracted)
        time.sleep(FLAGS.time_interval)
    # 如果只抓取最新的一条,只取第一页的第一条
    if FLAGS.single == 1:
        news_link_list = news_link_list[0:1]

    for idx, item in enumerate(news_link_list):
        news_content = get_url_content(item.url)
        extract_news_content(news_content, item)
        logging.info('[%03d][%s][%s]<%s>@[%s]', idx, item.news_time, item.content, item.title, item.url)
        analyze_news_content(item)
        send_news_content(item)
        time.sleep(FLAGS.time_interval)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='从中国人民银行网站抓取货币政策司的人民币汇率中间价公告')
    parser.add_argument('--num_pages', type=int, default=10, help='抓取多少页的公告,默认为10')
    parser.add_argument('--time_interval', type=float, default=0.5, help='两次抓取间隔的秒数,默认为0.5')
    parser.add_argument('--single', type=int, default=1, help='是否只抓取最新的一条,1为true,此时忽略--num_pages参数')
    parser.add_argument('--access_token', type=str, help='发送钉钉消息的参数,access_token,不填不发钉钉消息')
    parser.add_argument('--secret', type=str, help='发送钉钉消息的参数,secret,不填不发钉钉消息')
    FLAGS = parser.parse_args()
    main()
