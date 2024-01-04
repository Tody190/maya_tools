#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/12/27 13:56
# @Author  : YangTao


import requests
import json
import time
import shutil
import re
import os
import traceback
import sys


def go(graph_json, binary_zip_folder):
    print('\n--------------NEMO FARM--------------\n')
    url = "https://www.nemopuppet.com/api"
    message = {
        'username': os.environ.get('NEMO_FARM_USERNAME'),
        'password': os.environ.get('NEMO_FARM_PASSWORD'),
    }

    print(u'正在登陆到 %s\n' % url)
    recv = requests.post(url + '/login', data=message)
    auth = recv.cookies
    print(u'登录成功\n')

    files = {'file': open(graph_json, 'rb')}
    message = {'platform': 'Windows', 'gpu': True}
    recv = requests.post(url + '/tasks', data=message, files=files, cookies=auth)
    task_id = recv.json()['id']

    print(u'binary.zip 生成中，大概需要5到10分钟左右，请耐心等待...\n')
    start_time = time.time()
    while True:
        recv = requests.get('{}/task/{}'.format(url, task_id), cookies=auth)
        task_status = recv.json()['status']
        if task_status in {'Waiting', 'Running'}:
            time.sleep(20)
            print(task_status, u'已等待 %.2f 秒' % (time.time() - start_time))
        else:
            break

    if task_status == 'Success':
        print(u'\nbinary.zip 生成成功, 正在下载...')
        recv = requests.get(url + '/artifact/{}'.format(task_id), stream=True, cookies=auth)
        filename = re.findall('filename=\"(.+)\"', recv.headers['content-disposition'])[0]

        with open('{}/{}'.format(binary_zip_folder, filename), 'wb') as f:
            shutil.copyfileobj(recv.raw, f)

        print(u'binary.zip 下载成功')
    else:
        print(u'\nbinary.zip 生成失败')

    print('\n--------------NEMO FARM--------------')


if __name__ == '__main__':
    the_graph_json = sys.argv[1]
    the_binary_zip_folder = sys.argv[2]

    print('GRAPH JSON: %s' % the_graph_json)
    print('BINARY ZIP FOLDER: %s' % the_binary_zip_folder)

    with open(the_graph_json, 'r') as f:
        print('NEMO Version: %s' % json.load(f)['version'])

    try:
        go(the_graph_json, the_binary_zip_folder)
    except:
        print(u'\n---------失败了！找TD看看吧---------\n')
        print(traceback.format_exc())
        print(u'\n---------失败了！找TD看看吧---------\n')

    print(u'\n结束，请关闭窗口\n')