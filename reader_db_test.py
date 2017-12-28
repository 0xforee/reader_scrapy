#!/usr/bin/python3
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 foree <foree@foree-pc>
#
# Distributed under terms of the MIT license.

"""
测试db的可能值大小
"""
import requests
from bs4 import BeautifulSoup
import os
import logging
import re

log_dir="./log"
db_dir="./db"
base_url="http://m.piaotian.com"
www_base_url = "http://www.piaotian.com"
def get_url(url):
    # download url content
    try:
        r = requests.get(url)
        r.encoding = "gbk"
        r.raise_for_status
        return r.text
    except:
        logging.error("get %s error" % (r.url))
        return ""

def downloadchapter2file(chapter_url):
    print('chapter url = %s' % chapter_url)
    chapter_info = get_url(chapter_url)
    if len(chapter_info) > 0:
        soup = BeautifulSoup(chapter_info, 'html.parser')
        with open(os.path.join(db_dir, "chapter_db"), "a") as f:
            try:
                chapter_info = soup.find('div', id = 'nr1')
                chapter_info = re.sub(r'{飘天.*}', '',
                        chapter_info.get_text('\n\n'))
                f.write(chapter_info + "\n")
            except:
                logging.error("parser chapter_url chapter error")

def downloadlist2file(list_url):
    list_info = get_url(list_url)
    if len(list_info) > 0:
        soup = BeautifulSoup(list_info, "html.parser")
        with open(os.path.join(db_dir, "list_db"), "a") as f:
            for li in soup('li'):
                try:
                    if li.a and re.match(r'^[0-9a-z.]+$', li.a['href']):
                        chapter_url = list_url + li.a['href']
                        chapter_title = li.a.string
                    
                    # convert www_base_url to base_url for split chapter easily
                    chapter_url = chapter_url.replace(www_base_url, base_url)

                    f.write(chapter_url + " " + chapter_title + "\n")
                    if chapter_url:
                        downloadchapter2file(chapter_url)
                except :
                    logging.error("parser %s error" % li)


def download_book_info(url):
    content = get_url(url)
    info=[]
    if len(content) > 0:
        soup = BeautifulSoup(content, "html.parser")
        try:
            # find book info
            block = soup.find('div', 'block')
            print('cover_img = %s' % (block.img['src']))

            book_info = block.find('div', 'block_txt2')
            for child in book_info('p'):
                item = ''
                if child.string:
                    info.append(child.string)
                    print(child.string)
                else:
                    for string in child.strings:
                        item = item + string
                    info.append(item)
                    print(item)

            # get content url
            list_url = www_base_url + soup('span')[1].a['href'].replace('index.html', '')
            print('章节目录:' + list_url)
        except:
            pass

        if list_url:
            # use www_base_url for get content only once
            downloadlist2file(list_url)

def init():
    # create dir if not exits
    global log_dir
    global db_dir
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    if not os.path.exists(db_dir):
        os.mkdir(db_dir)
    
    # init logging config
    message_fmt="%(asctime)s %(process)d %(levelname)s/%(funcName)s(%(lineno)d): %(message)s"
    datefmt="%Y-%m-%d %H:%M:%S"
    logging.basicConfig(filename="/var/log/reader_db.log", level=logging.INFO, format=message_fmt, datefmt=datefmt)


def main():
    # init
    init()

    # generate url
    for page_index in range(1, 2):
        url = base_url + '/top/allvote_' + str(page_index)
        #url = "http://www.piaotian.com/booktopallvisit/0/" + str(page_index) + ".html"
        print("get %s starting..." % url )
        content = get_url(url)
        if len(content) > 0:
            soup = BeautifulSoup(content, "html.parser")
            for line in soup('a', 'blue'):
                try:
                    info_url = line['href']
                except:
                    info_url = None

                if info_url:
                    download_book_info(base_url + info_url)
        logging.info("get %s done." % (url))
        print("get %s done. " % (url))


if __name__ == '__main__':
    main()
