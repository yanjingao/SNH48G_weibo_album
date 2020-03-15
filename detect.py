# -*- coding:utf-8 -*-

from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import requests

def detect(root_in, root_out, list_file, i):
    name = list_file[i][:-4]
    len_null = int(20 - int((len(name.encode('utf-8')) - len(name)) / 2 + len(name)))
    path_in = root_in + list_file[i]
    path_out = root_out + list_file[i]
    url_api = 'https://api-cn.faceplusplus.com/facepp/v3/detect'
    key = '9EQg6Fsz_TViCPRSbVs525VNhdadwF8F'
    secret = 'pNBKgZ98Iu8Rp8vFSBXJNO1A5KuHbvY5'
    with open(path_in, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    list_url_pic_good = []
    for j in range(len(lines)):
        try:
            url_pic = lines[j][:-1]
            url_pic_mw690 = url_pic.replace("large", "mw690")
            data = {'api_key': key, 'api_secret': secret, 'image_url': url_pic_mw690}
            while True:
                r = requests.post(url_api, data=data)
                res = eval(r.text)
                if 'error_message' not in res or res['error_message'] != 'CONCURRENCY_LIMIT_EXCEEDED':
                    break
            if len(res['faces']) > 0:
                list_url_pic_good.append(url_pic + '\n')
            print('\r[%3d/%3d][%5d/%5d] %s - %5d - %3.2f%%' % (i + 1, len(list_file), j + 1, len(lines), name + ' ' * len_null, len(list_url_pic_good), (j + 1) / len(lines) * 100), end='')
        except:
            pass
    print('\r[%3d/%3d][%5d/%5d] %s 过滤完成！                        ' % (i + 1, len(list_file), len(list_url_pic_good), len(lines), name + ' ' * len_null))
    if len(list_url_pic_good) > 0:
        with open(path_out, 'w', encoding='utf-8') as f:
            f.writelines(list_url_pic_good)

if __name__ == '__main__':

    root_in = 'SNH48所有成员微博图片链接/'
    root_out = 'SNH48所有成员微博图片链接（含人脸）/'

    if not os.path.exists(root_out):
        os.mkdir(root_out)
    list_file = os.listdir(root_in)
    with ThreadPoolExecutor(max_workers=2) as executor:
        list_thread = []
        for i in range(len(list_file)):
            list_thread.append(executor.submit(detect, root_in, root_out, list_file, i))