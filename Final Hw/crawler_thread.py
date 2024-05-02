# SJTU EE208

import os
import re
import string
import sys
import threading
import queue
import time
import BloomFilter
import urllib.error
import urllib.parse
import requests
import jieba
import chardet

import sqlite3
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

import logging
logging.basicConfig(filename='crawler.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s:%(message)s')
from joblib import load
model = load('model.joblib')


num = 8
q = queue.Queue()
count = 0
dblock = threading.Lock()
varlock = threading.Lock()
indexlock = threading.Lock()
htmllock= threading.Lock()
bflock = threading.Lock()
cntlock = threading.Lock()
isprint = False
thread_activity = {}

with open('stopwords.txt', 'r', encoding='utf-8') as f:
    stopwords = set([w.strip() for w in f.readlines()])
    
    
def get_publish_date(content):
    soup = BeautifulSoup(content, 'lxml')
    date_element = soup.find('div', class_='publish-date')
    return date_element.get_text(strip=True) if date_element else None

def create_db_connection():
    conn = sqlite3.connect('crawled_data.db')
    return conn

def initialize_database(connection):
    try:
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS sports_pages (
                            id INTEGER PRIMARY KEY,
                            url TEXT NOT NULL,
                            title TEXT,
                            content TEXT,
                            published_date DATE)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS finance_pages (
                            id INTEGER PRIMARY KEY,
                            url TEXT NOT NULL,
                            title TEXT,
                            content TEXT,
                            published_date DATE)''')
        connection.commit()
    except Exception as e:
        print(f"Error in initialize_database: {str(e)}")
    finally:
        cursor.close()

def get_page(page):
    try:
        # 发送请求
        req = urllib.request.Request(page)
        req.add_header('User-Agent', "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0")
        response = urllib.request.urlopen(req)
        
        content_type = response.headers.get('Content-Type', '')
        
        # 读取原始字节内容
        rawdata = response.read()
        
        if 'text' in content_type:
        # 尝试使用常见编码进行解码
            try_encodings = ['utf-8', 'gbk', 'iso-8859-1']
            for encoding in try_encodings:
                try:
                    return rawdata.decode(encoding)
                except UnicodeDecodeError:
                    continue

        # 如果常见编码都失败了，使用chardet检测编码
            encoding = chardet.detect(rawdata)['encoding']
            if encoding:
                return rawdata.decode(encoding)
            else:
                return rawdata.decode('utf-8', errors='ignore')
            
        else:
            # 对于非文本内容，跳过编码处理
            return rawdata
    except Exception as e:
        logging.error(f"Error in get_page: {str(e)}")
        return None

def get_all_links(content, page):
    if content == None:
        return []
    links = []
    soup = BeautifulSoup(content, features="lxml")
    for link in soup.find_all('a', href=True):  # 获取所有带href属性的<a>标签
        mylink = link.get("href")

        # 过滤掉不需要的链接类型，如JavaScript链接
        if mylink.startswith('javascript:') or mylink.startswith('#'):
            continue

        # 处理以'//'开头的协议相对URL
        if mylink.startswith('//'):
            mylink = 'http:' + mylink

        # 将相对链接转换为绝对链接
        elif mylink.startswith("/"):
            mylink = urllib.parse.urljoin(page, mylink) 
        badlink = ['leju','db.auto','astro']
        if not any (word in mylink for word in badlink):
            links.append(mylink)
    #print(links)
    return links

def union_dfs(a, b):
    for e in b:
        if e not in a:
            a.append(e)
            
def union_bfs(a, b):
    for e in b:
        if e not in a:
            a.insert(0,e)


def add_page_to_database(page, content,label): 
    #print(label)    
    
    #with open('temp.txt', 'w', encoding='utf-8') as temp_file:
    #    temp_file.write(content)

    title = re.search(r'<title>.*?</title>', content)
    title_str = title.group()[7:-8] if title else ''
    
    publish_date = get_publish_date(content)

    table_name = "sports_pages" if label == 's' else "finance_pages"
    #print(table_name)
    
    precontent = preprocess_content(content)
        
    conn = create_db_connection()
    try:
        c = conn.cursor()
        c.execute(f"INSERT OR IGNORE INTO {table_name} (url, title, content,published_date) VALUES (?, ?, ?,?)",
                  (page, title_str, precontent,publish_date))
        conn.commit()
        c.close()
    except Exception as e:
        logging.error(f"Error in add_page_to_database: {str(e)}")
    finally:
        conn.close()

def preprocess_content(content):
    # 清洗文本
    content = re.sub(r'[^\u4e00-\u9fa5]', '', content)

    # 分词
    words = jieba.cut(content)

    # 去除停用词
    filtered_words = [word for word in words if word not in stopwords]

    # 返回处理后的文本
    return ' '.join(filtered_words)

def crawl(thread_id):
    global count,isprint,bf,max_page,max_depth,thread_activity
    
    crawled = set()
    while count < max_page and not q.empty() :
        thread_activity[thread_id] = time.time()
        try:
            page,depth = q.get(timeout=3)
        except queue.Empty:
            break
        if page not in crawled and depth <= max_depth:
            cntlock.acquire()
            print(count,page)
            cntlock.release()
            content = get_page(page)
            if not isinstance(content,str):
                continue
            processed_content = preprocess_content(content) # 根据模型的需要进行适当的预处理

            # 使用模型进行预测
            prediction = model.predict([processed_content])
            #print(prediction)

            # 检查是否为体育类内容
            if prediction == '体育类' :
                add_page_to_database(page, content,'s')
            elif prediction == '财经类':
                add_page_to_database(page,content,'f')
                
            outlinks = get_all_links(content, page)
            for link in outlinks:
                q.put((link,depth+1))
            bflock.acquire()
            bf.add(page)
            bflock.release()
            cntlock.acquire()
            count+=1
            cntlock.release()
            
            crawled.add(page)
            
    return 
            
def monitor_threads():
    global thread_activity
    while True:
        time.sleep(60)  # 每60秒检查一次
        current_time = time.time()
        for thread_id, last_active in thread_activity.items():
            if current_time - last_active > 300:  # 设定阈值，例如5分钟
                logging.warning(f"Thread {thread_id} is inactive, restarting.")

if __name__ == '__main__':

    try:
        # 主程序...
        seed = 'https://finance.sina.com.cn/'
        max_page = 5000
        max_depth = 10  # 可以根据需要设置深度
    
        q.put((seed, 0)) 
        
        conn = create_db_connection()
        initialize_database(conn) 

        bf = BloomFilter.BloomFilter(max_page, 0.1)

        for i in range(num):
            thread_activity[i] = time.time()
            thread = threading.Thread(target=crawl, args=(i,))
            thread.start()

        # 启动监控器线程
        monitor_thread = threading.Thread(target=monitor_threads)
        monitor_thread.start()
    except Exception as e:
        logging.error(f"Fatal error in main loop: {str(e)}")
