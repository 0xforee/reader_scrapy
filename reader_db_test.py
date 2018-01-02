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

book = None


class Book():
    host = {}
    name = ''
    author = ''
    url = ''
    update_time = ''
    cover_url = ''
    category = ''
    contents_url = ''
    contents = []
    description = ''

    def __init__(self):
        contents = []
        pass

    def set_contents(self, contents):
        self.contents = contents

    def add_chapter(self, chapter):
        print('add chapter')
        self.contents.append(chapter)

    def parse_book_info(self, info):
        if info.find('：') != -1:
            if info.find('作者') != -1:
                self.author = info.split('：')[1].strip()
            elif info.find('分类') != -1:
                self.category = info.split('：')[1].strip()
            elif info.find('更新') != -1:
                self.update_time = info.split('：')[1].strip()
        else:
            self.name = info

    def set_content_url(self, content_url):
        self.content_url = content_url

    def set_url(self, url):
        self.url = url

    def set_cover_url(self, url):
        self.cover_url = url

    def insert_db(selft):
        book = {
                'host': self.host,
                'name': self.name,
                'author': self.author,
                'url': self.url,
                'update_time': self.update_time,
                'cover_url': self.cover_url,
                'category': self.category,
                'contents_url': self.contents_url,
                'contents': self.contents,
                'description': self.description
        }
        # insert mongodb
        pass


def set_chapter(chapter_name, chapter_url):
    chapter = {
            'name': chapter_name,
            'url': chapter_url}

    return chapter

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
    global book
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
    global book
    i = 0
    list_info = get_url(list_url)
    #print(list_info)
    if len(list_info) > 0:
        soup = BeautifulSoup(list_info, "html.parser")
        with open(os.path.join(db_dir, "list_db"), "a") as f:
            for li in soup('li'):
                try:
                    if li.a and re.match(r'^[0-9a-z.]+$', li.a['href']):
                        print('get chapter starting...')
                        chapter_url = list_url + li.a['href']
                        chapter_title = li.a.string
                    
                        # convert www_base_url to base_url for split chapter easily
                        chapter_url = chapter_url.replace(www_base_url, base_url)

                        chapter = set_chapter(chapter_title, chapter_url)
                        book.add_chapter(chapter)

                        f.write(chapter_url + " " + chapter_title + "\n")
                        if chapter_url:
                            #downloadchapter2file(chapter_url)
                            pass
                        i = i+1
                        if i > 10:
                            return
                except Exception as e:
                    print('parse error ' + str(e))
                    logging.error("parser %s error  = " % (li) + str(e))


def download_book_info(url):
    global book
    content = get_url(url)
    info=[]
    if len(content) > 0:
        soup = BeautifulSoup(content, "html.parser")
        try:
            # find book info
            block = soup.find('div', 'block')
            print('cover_img = %s' % (block.img['src']))
            book.set_cover_url(block.img['src'])

            book_info = block.find('div', 'block_txt2')
            for child in book_info('p'):
                item = ''
                if child.string:
                    info.append(child.string)
                    print(child.string)
                    book.parse_book_info(child.string)
                else:
                    for string in child.strings:
                        item = item + string
                    info.append(item)
                    print(item)
                    book.parse_book_info(item)

            # get content url
            list_url = www_base_url + soup('span')[1].a['href'].replace('index.html', '')
            print('章节目录:' + list_url)

            if list_url:
                # use www_base_url for get content only once
                book.set_content_url(list_url)
                downloadlist2file(list_url)
        except Exception as e:
            print("error = " + str(e))


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
        # init book
        global book

        print("get %s starting..." % url )
        content = get_url(url)
        if len(content) > 0:
            soup = BeautifulSoup(content, "html.parser")
            for line in soup('a', 'blue'):
                book = Book()
                try:
                    info_url = line['href']
                except:
                    info_url = None

                if info_url:
                    download_book_info(base_url + info_url)
                    book.set_url(base_url + info_url)
                print(book.__dict__)
                print(book.contents)
        logging.info("get %s done." % (url))
        print("get %s done. " % (url))


if __name__ == '__main__':
    main()
