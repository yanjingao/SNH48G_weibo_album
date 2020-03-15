# -*- coding:utf-8 -*-

from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import os


def download(i, url, root):
    path = root + url.split('/')[-1]
    r = requests.get(url)
    with open(path, 'wb') as f:
        f.write(r.content)
    return i


if __name__ == '__main__':

    root = 'C:/Users/shu/Desktop/图片/'
    path_url = '图片链接（含人脸）.txt'

    if not os.path.exists(root):
        os.mkdir(root)

    with open(path_url, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    with ThreadPoolExecutor(max_workers=10) as executor:
        list_thread = []
        for i in range(len(lines)):
            list_thread.append(executor.submit(download, i, lines[i][:-1], root))
        for future in as_completed(list_thread):
            i = future.result()
            print("\r[%d/%d]正在下载！" % (i + 1, len(lines)), end="")

    print('\n下载完成！')
