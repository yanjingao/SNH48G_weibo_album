# -*- coding:utf-8 -*-

from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time
import requests
import json
from bs4 import BeautifulSoup
import os

def get(i, uid, name, cookies):
    list_pic = []
    for j in range(1, 10000):
        url_api = 'http://photo.weibo.com/photos/get_all?uid=%s&count=32&page=%d&type=3' % (uid, j)
        while True:
            try:
                print('\r[%3d] %s' % (i + 1, name), end='')
                r = requests.get(url_api, cookies=cookies, timeout = 10)
                break
            except:
                continue
        r.encoding = r.apparent_encoding
        try:
            dict_return = json.loads(r.text)
        except:
            break
        photo_list = dict_return['data']['photo_list']
        if len(photo_list) == 0:
            break
        for pic in photo_list:
            url_pic = pic['pic_host'] + '/large/' + pic['pic_name']
            if url_pic.endswith('.jpg'):
                list_pic.append(url_pic)
        print('\r[%3d] %s：已解析%d页、%d张jpg图片！            ' % (i + 1, name, j + 1, len(list_pic)), end='')
    return i, name, list_pic

if __name__ == '__main__':

    root = 'SNH48所有成员微博图片链接/'
    UserName = '0084947183828'
    PassWord = '13307008755'

    time_start = time.time()

    print('正在获取成员微博地址......')
    names = []
    uids = []
    url_api = 'http://h5.snh48.com/resource/jsonp/allmembers.php?gid=00&callback=get_members_success'
    r = requests.post(url_api)
    r.encoding = r.apparent_encoding
    success = 'get_members_success'
    if r.text.startswith(success):
        dict_return = json.loads(r.text[len(success) + 1:-2])
        for member in dict_return['rows']:
            if member['status'] != '44':
                names.append(member['gname'] + '48-' + member['sname'])
                uids.append(member['weibo_uid'])
        print('成功获取%d个成员的微博地址！' % len(uids))
    else:
        print('api出错！')

    print("正在登录......")
    browser = webdriver.Chrome()
    browser.maximize_window()
    wait = WebDriverWait(browser, 10)
    browser.get('https://weibo.com')
    username = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#loginname')))
    password = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#pl_login_form > div > div:nth-child(3) > div.info_list.password > div > input')))
    loginbutton = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#pl_login_form > div > div:nth-child(3) > div.info_list.login_btn > a')))
    time.sleep(1)
    username.send_keys(UserName)
    time.sleep(1)
    password.send_keys(PassWord)
    time.sleep(1)
    loginbutton.click()
    time.sleep(3)
    while True:
        try:
            code = WebDriverWait(browser, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#pl_login_form > div > div:nth-child(3) > div.info_list.verify.clearfix > div > input')))
            Code = input('登录失败！请输入验证码：')
            code.send_keys(Code)
            loginbutton.click()
            time.sleep(3)
        except:
            print('登录成功！成功获取cookies！')
            break
    cookies = {}
    for cookie in browser.get_cookies():
        cookies[cookie['name']] = cookie['value']
    browser.quit()

    if not os.path.exists(root):
        os.mkdir(root)
    with ThreadPoolExecutor(max_workers=100) as executor:
        list_thread = []
        for i in range(len(uids)):
            list_thread.append(executor.submit(get, i, uids[i], names[i], cookies))
        for future in as_completed(list_thread):
            i, name, list_pic = future.result()
            path_url = root + names[i] + '.txt'
            if len(list_pic) > 0:
                with open(path_url, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(list_pic) + '\n')
            len_null = int(20 - int((len(names[i].encode('utf-8')) - len(names[i])) / 2 + len(names[i])))
            print('\r[%3d/%3d] %s：成功解析%5d张jpg图片！\n' % (i + 1, len(uids), names[i] + ' ' * len_null, len(list_pic)), end='')

    time_end = time.time()
    interval = int(time_end-time_start)
    s = interval % 60
    interval = int(interval/60)
    m = interval % 60
    interval = int(interval/60)
    h = interval
    print('处理完成！已用时%02d:%02d:%02d！' % (h, m, s))
