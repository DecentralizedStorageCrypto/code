import xml.etree.ElementTree as ET
import requests
import time
import newspaper
import datetime
import pandas as pd
from db import mongodb
import threading
import sys


localhost = "mongodb://127.0.0.1:27017"
db_name = "players"
mng = mongodb(localhost, db_name)
collection_name = "entities"

#loading the rss page
def loadPage(url, fileName=None):

    flag = False
    # setting the headers of request to get the latest news of rss feed
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    resp = requests.get(url, timeout=20, headers=headers)
    if resp.status_code == 200:
        # saving the xml file
        with open(fileName, 'wb') as f:
            f.write(resp.content)
            f.close()
            flag = True
            return flag
    else:
        return flag

#parsing xml file

def parseXML(xmlfile, entity):

    tree = ET.parse(xmlfile)
    #get root element of xml file
    root = tree.getroot()
    #iterate over news items of xml file

    for item in root:
        for item in item.findall('item'):
            for child in item:
                if child.tag == 'link':
                    url = child.text
                    print(url)
                elif child.tag == 'pubDate':
                    publish_date = child.text
                    print(entity)
                    print(publish_date)
            try:
                doc = newspaper.Article(url=url, language='en')
                doc.download()
                doc.parse()
                doc = {
                    "title": str(doc.title),
                    "text": str(doc.text),
                    "authors": doc.authors,
                    "published_date": publish_date,
                    "top_image": str(doc.top_image),
                    "link": url,
                    "entity": entity
                }
                #print(doc)
                writeToDb(doc)
            except Exception as e:
                print(str(e))
                pass

#write to the orresponding collection of mongodb
def writeToDb(doc):
    mng.writeOne("newsByNode2", doc)

def newsScrapper(tid, entity):

    print(tid)
    s_lst = "2022/12/01".split('/')
    # defining start date
    start_date = datetime.date(int(s_lst[0]), int(s_lst[1]), int(s_lst[2]))
    #print(start_date)
    # defining end date
    f_lst = "2023/01/01".split('/')
    finish_date = datetime.date(int(f_lst[0]), int(f_lst[1]), int(f_lst[2]))
    #print(finish_date)
    # defining a list of dates within the defined range
    BASE_URL = 'https://news.google.com/rss'
    query = 'allintitle:{}'.format(entity) + ' ' + 'after:{}'.format(start_date) + ' ' + 'before:{}'.format(finish_date)
    #print(query)
    URL = BASE_URL + '/search?q={}'.format(query)
    filename = 'info12/{}_news.xml'.format(entity)
    flag = loadPage(URL, filename)
    if flag:
        print('successfully done')
        parseXML(filename, entity)

#calling main to collect latest news of the feed web page
if __name__ == "__main__":
    df = mng.returnColAsDf(collection_name)
    entity_list = []
    for counter in range(df.shape[0]):
        if df.iloc[counter]['category'] != 'influencer':
            entity_list.append(df.iloc[counter]['player'])
    print(entity_list)
    num_entity = len(entity_list)
    batch_size = 5
    res = num_entity % batch_size
    print(res)
    phases = int(num_entity / batch_size)
    print(phases)
    for counter in range(phases):
        can_list = entity_list[counter*batch_size:(counter+1)*batch_size]
        print("current list is:", can_list)
        threads = []
        for i in range(len(can_list)):
            #print(can_list[i])
            threads.append(threading.Thread(target=newsScrapper, args=(i, can_list[i])))
            threads[i].start()
        for j in range(len(can_list)):
            threads[j].join()
        print("counter is:", counter)
        print("waiting...")
        time.sleep(2)
    if res != 0:
        can_list = entity_list[-res:]
        threads = []
        for i in range(len(can_list)):
            threads.append(threading.Thread(target=newsScrapper, args=(i, can_list[i])))
            threads[i].start()
        for j in range(len(can_list)):
            threads[j].join()