#! /usr/bin/env python
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

log_dir="./log"
db_dir="./db"
base_url="http://m.piaotian.com"
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
	chapter_info = get_url(chapter_url)
	if len(chapter_info) > 0:
		with open(os.path.join(db_dir, "chapter_db"), "a") as f:
			try:
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
                    chapter_url = list_url + li.a['href']
                    chapter_title = li.a.string
                    f.write(chapter_url + " " + chapter_title + "\n")
                    if chapter_url:
                    	downloadchapter2file(chapter_url)
                except :
                    logging.error("parser %s error" % li)


def download_book_info(url):
    content = get_url(url)
    if len(content) > 0:
        soup = BeautifulSoup(content, "html.parser")
        for line in soup('a', 'blue'):
            try:
                info_url = line['href']
            except:
                info_url = None

            if info_url:
                downloadlist2file(base_url + info_url)
#        with open(os.path.join(db_dir, "reader_db"), "a") as f:
#            for tr in soup("tr"):
#                for th in tr("th"):
#                    f.write(th.string + " ")
#                for td in tr("td"):
#                    f.write(td.string + " ")
#                f.write("\n")
#                try:
#                    info_url = tr.td.a['href']
#                except:
#                    info_url = None
#                if info_url:
#                    list_url = info_url.replace("bookinfo", "html").replace(".html", "/")
#                    downloadlist2file(list_url)


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
    for page_index in range(1,463):
        url = 'http://m.piaotian.com/top/allvote_' + str(page_index)
        #url = "http://www.piaotian.com/booktopallvisit/0/" + str(page_index) + ".html"
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


main()
