import re

import sys
from bs4 import BeautifulSoup
import requests
import pymongo
import time
from multiprocessing import Pool

import chardet



client = pymongo.MongoClient('localhost',27017)
jinjiang_db = client['jinjiang_db']
jinjiang_url_list = jinjiang_db['jinjiang_url_list']
jinjiang_like_list = jinjiang_db['jinjiang_like_list']
# url = 'http://wap.jjwxc.net/pindao/vip'
# header = {
#     'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
# }


def getUrls(page):
    print (jinjiang_url_list.count())
    url = 'http://wap.jjwxc.net/pindao/vip/page/{}'.format(str(page))
    wb_data = requests.get(url)
    soup = BeautifulSoup(wb_data.text, 'lxml')
    #body > div.grid-c > div:nth-child(7) > ul > li:nth-child(1) > a:nth-child(2)
    jinjiang_urls = soup.select('body > div.grid-c > div > ul > li > a:nth-of-type(2)')
    for jinjiang_url in jinjiang_urls:
        data = {
            "url": "http://wap.jjwxc.net"+jinjiang_url.get('href')
        }
        jinjiang_url_list.insert_one(data)
#left > li:nth-child(5)

def getLikeNumber(url):
    try:
        time.sleep(0.1)
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'lxml')
        #print (soup)
        #body > div.grid - c > div:nth - child(9) > h2
        names = soup.select('h2.big.o')
        stars = soup.select('div#left > li:nth-of-type(5)')
        types = soup.select('div#left > li:nth-of-type(2)')
        #novelintro
        describes = soup.select('li#novelintro')
        result = names[0].get_text().split('>')[1:]

# print (result[0])
        # print (re.findall(r'\d+',stars[0].get_text())[0])
        # print (types[0].get_text())
        star = re.findall(r'\d+', stars[0].get_text())[0].encode('latin-1').decode('gbk')
        data = {
            'name' : result[0].encode('latin-1').decode('gbk'),
            'star' : int(star),
            'type' : types[0].get_text().encode('latin-1').decode('gbk'),
            'describe' : describes[0].get_text().encode('latin-1').decode('gbk'),
            'url' : url
        }
        jinjiang_like_list.insert_one(data)
        print (jinjiang_like_list.count())
    except:
        print ('error')

def get_all_item_info(urls):
    for url in urls:
        getLikeNumber(url)

def crawling():
    for page in range(1,1346):
        getUrls(page)
    #getLikeNumber('http://wap.jjwxc.net/book2/1984245')
    db_urls = [item['url'] for item in jinjiang_url_list.find()]
    index_urls = [item['url'] for item in jinjiang_like_list.find()]
    x = set(db_urls)
    y = set(index_urls)
    rest_of_urls = x - y
    pool = Pool(processes=4)
    pool.apply(get_all_item_info(rest_of_urls))

if __name__ == "__main__":
    # for page in range(1,1346):
    #     getUrls(page)
    #getLikeNumber('http://wap.jjwxc.net/book2/1984245')
    # db_urls = [item['url'] for item in jinjiang_url_list.find()]
    # index_urls = [item['url'] for item in jinjiang_like_list.find()]
    # x = set(db_urls)
    # y = set(index_urls)
    # rest_of_urls = x - y
    # pool = Pool(processes=4)
    # pool.apply(get_all_item_info(rest_of_urls))
    # #.sort('star', pymongo.DESCENDING).limit(50)
    # for name in jinjiang_like_list.find():
    #     star = int(name['star'])
    #     print (type(star))
    #     jinjiang_like_list.update_one({'url': name['_id']}, {"$set": {'star': star}})
    #     print ("after: ")
    #     print (type(name['star']))
    #     print ('name:'+name['name']+", stars:"+name['star']+",type:"+name['type']+",url:"+name['url'])
    crawling()
    jinjiang_like_list.distinct('name')
    for name in jinjiang_like_list.find().sort('star', -1).limit(300):
        print ('name:' + name['name'] + ", stars:" + str(name['star']) + ",type:" + name['type'].strip() + ",url:" + name['url'])
        print ('description:' + name['describe'])



