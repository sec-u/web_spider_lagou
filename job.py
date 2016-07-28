#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# @Time    : 16-7-11 下午7:51
# @Author  : leon
# @Site    : 
# @File    : test1.py
# @Software: PyCharm

import requests
from bs4 import BeautifulSoup

origin = 'http://www.lagou.com'
cookie = 'Cookie: user_trace_token=20160615104959-0ac678b0e03a46c89a313518c24ff856; LGMOID=20160710094357-447236C62C36EDA1D297A38266ACC1C3; LGUID=20160710094359-c5cb0e3b-463f-11e6-a4ae-5254005c3644; index_location_city=%E6%9D%AD%E5%B7%9E; LGRID=20160710094631-208fc272-4640-11e6-955d-525400f775ce; _ga=GA1.2.954770427.1465959000; ctk=1468117465; JSESSIONID=F827D8AB3ACD05553D0CC9634A5B6096; SEARCH_ID=5c0a948f7c02452f9532b4d2dde92762; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1465958999,1468115038; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1468117466'
user_agent = 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'
headers = {'cookie':cookie,
           'origin':origin,
           'User-Agent':user_agent,
           }

url = 'http://www.lagou.com'
r = requests.get(url=url, headers=headers)
page = r.content.decode('utf-8')
soup = BeautifulSoup(page, 'lxml')
date = []

jobnames = soup.select('#sidebar > div.mainNavs > div > div.menu_sub.dn > dl > dd > a')
for i in jobnames:
    jobname = i.get_text().replace('/','+')
    date.append(jobname)

with open('jobnames', 'w') as f:
    for i in date:
        f.write(i + '\n')

