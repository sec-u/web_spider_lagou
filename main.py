#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# @Time    : 16-7-10 下午1:18
# @Author  : leon
# @Site    : 
# @File    : main.py
# @Software: PyCharm

import requests
import json
from elasticsearch import Elasticsearch
from datetime import datetime
from queue import Queue
from threading import Thread
import time
import random


class MyThread(Thread):
    def __init__(self, func):
        super(MyThread, self).__init__()
        self.func = func

    def run(self):
        self.func()


class Lagou(object):
    def __init__(self, positionname, start_num=1):
        # 定义origin headers参数
        self.origin = 'http://www.lagou.com'
        # 定义cookie headers参数
        self.cookie = ("Cookie: ctk=1468304345; "
                       "JSESSIONID=7EEE619B6201AF72DEDDD895B862B2A0; "
                       "LGMOID=20160712141905-A5E4B025F73A2D76BC116066179D097C; _gat=1; "
                       "user_trace_token=20160712141906-895f24c3-47f8-11e6-9718-525400f775ce; "
                       "PRE_UTM=; PRE_HOST=; PRE_SITE=; PRE_LAND=http%3A%2F%2Fwww.lagou.com%2F; "
                       "LGUID=20160712141906-895f278b-47f8-11e6-9718-525400f775ce; "
                       "index_location_city=%E5%85%A8%E5%9B%BD; "
                       "SEARCH_ID=4b90786888e644e8a056d830e2c332a1; "
                       "_ga=GA1.2.938889728.1468304346; "
                       "Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1468304346; "
                       "Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1468304392; "
                       "LGSID=20160712141906-895f25ed-47f8-11e6-9718-525400f775ce; "
                       "LGRID=20160712141951-a4502cd0-47f8-11e6-9718-525400f775ce")
        # 定义user_agent headers参数
        self.user_agent = ('User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                           '(KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36')
        # 定义referer headers参数
        self.referer = 'http://www.lagou.com/zhaopin/Python/?labelWords=label'
        # 定义headers
        self.headers = {'cookie': self.cookie,
                        'origin': self.origin,
                        'User-Agent': self.user_agent,
                        'Referer': self.referer,
                        'X-Requested-With': 'XMLHttpRequest'
                        }
        # 定义url
        self.url = 'http://www.lagou.com/jobs/positionAjax.json?'
        # 实例化Queue 存放post data
        self.date_post = Queue()
        # 实例化Queue 存放dict data
        self.date_dict = Queue()
        # 实例化连接es
        self.es = Elasticsearch(hosts='192.168.30.10')
        # es索引名字
        self.es_index_name = 'lagou'
        # 开始page数值
        self.page_number_start = start_num
        # 定义Job name
        self.positionName = positionname
        # 定义socks5代理
        self.proxies0 = {
            'http': 'socks5://127.0.0.1:1080'
        }
        self.proxies1 = {
            'http': 'socks5://127.0.0.1:1081'
        }
        self.proxies2 = {
            'http': 'socks5://127.0.0.1:1082'
        }
        self.proxies3 = {
            'http': 'socks5://127.0.0.1:1083'
        }
        self.proxies4 = {
            'http': 'socks5://127.0.0.1:1084'
        }
        self.proxies5 = {
            'http': ''
        }

    def post_date(self, n):
        """生成post data 并放入实例化的Queue"""
        date = {'first': 'true',
                'pn': n,
                'kd': self.positionName}
        self.date_post.put(date)

    def code(self, date):
        """随机选择代理点post连接，并返回数据"""
        try:
            proxies_list = (self.proxies0, self.proxies1, self.proxies2,
                            self.proxies3, self.proxies4, self.proxies5)
            proxies = random.choice(proxies_list)
            print(proxies)
            request = requests.post(url=self.url, headers=self.headers,
                                    params=date, proxies=proxies, timeout=15)
            date_str = request.content.decode('utf-8')
            return date_str
        except:
            # 执行失败，date 重新放回Queue
            print('请求出错')
            self.date_post.put(date)

    def json_dict(self, date_str, n):
        """由原始的数据，解析出有用的数据"""
        try:
            dict_date = json.loads(date_str)
            date_list = dict_date['content']['positionResult']['result']
            if len(date_list) == 0:
                # 爬取完毕
                return 0
            else:
                # put下一次要爬取的页码
                n += 1
                self.post_date(n)
                return date_list
        except:
            print(date_str)
            return None

    def dict_put(self, date_list):
        """由列表解析字典，添加时间字段，并放入Queue"""
        for i in date_list:
            i['@timestamp'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')
            i['Jobname'] = self.positionName
            self.date_dict.put(i)

    def work_date(self):
        """执行函数，获取数据"""
        while True:
            time.sleep(10)
            # 获取post data
            date = self.date_post.get()
            num = date['pn']
            print(num, self.positionName)
            self.date_post.task_done()
            # 获取原始data
            date_str = self.code(date)
            if date_str:
                date_list = self.json_dict(date_str, num)
            else:
                continue
            if None:
                self.date_post.put(date)
                continue
            elif date_list == 0:
                # 爬取完毕 break循环
                break
            else:
                self.dict_put(date_list)

    def es_index(self, dict_data):
        """数据插入es"""
        try:
            print(dict_data)
            self.date_dict.task_done()
            # 获取唯一id 作为es文档id
            es_id = dict_data['positionId']
            # 转换为json
            date = json.dumps(dict_data)
            self.es.index(index=self.es_index_name, doc_type='job', id=es_id, body=date)
        except:
            # 执行失败，重新放回Queue
            print(dict_data)
            time.sleep(5)
            self.date_dict.put(dict_data)

    def work_es(self):
        """数据插入执行函数"""
        while True:
            dict_data = self.date_dict.get()
            self.es_index(dict_data)

    def run(self):
        # 添加post data到Queue
        self.post_date(self.page_number_start)
        thread_date = MyThread(self.work_date)
        # thread_date.setDaemon(True)
        thread_date.start()
        for _ in list(range(5)):
            thread_es = MyThread(self.work_es)
            thread_es.setDaemon(True)
            thread_es.start()
        thread_date.join()
        self.date_post.join()
        self.date_dict.join()


if __name__ == '__main__':
    with open('jobnames', 'r') as f:
        job_list = f.readlines()

    for i in job_list:
        name = i.strip('\n')
        x = Lagou(positionname=name)
        x.run()

