import xml.etree.ElementTree as ET
import requests
import time
import newspaper
import datetime
import pandas as pd
from db import mongodb
import threading
import sys
from preprocessing import textProcessing



localhost = "mongodb://127.0.0.1:27017"
db_name = "players"
txtprc = textProcessing()
mng = mongodb(localhost, db_name)
collection_name = "relations"

def computeScore(e1, e2, linkStatus):
    df_exc = mng.returnColAsDf("excludeWords")
    exc_list = df_exc['word'].to_list()
    epsilon = 0.2
    title_pos = 1.5
    snip_pos = 1
    url_pos = 0.5
    null = None
    lst = (list(eval((linkStatus))))
    title_final_score = 0
    try:
        for j in range(len(lst) - 1):
            tmp_title_score = 0
            title = lst[j]['title']
            tokens = txtprc.normalizing(title)
            # print(tokens)
            for w in exc_list:
                if w in tokens:
                    tmp_title_score -= epsilon
                    # print(w)
            # print("after removing exclude words -->", tmp_title_score)
            if tmp_title_score > -epsilon:
                p2_lst = e2.lower().split(" ")
                # print(p2_lst)
                if len(p2_lst) > 1:
                    if e1 in tokens and p2_lst[0] in tokens and p2_lst[1] in tokens:
                        tmp_title_score += title_pos
                else:
                    if e1 in tokens and p2_lst[0] in tokens:
                        tmp_title_score += title_pos
            # print("final ->", tmp_title_score)
            title_final_score += tmp_title_score
    except Exception as e:
        print(str(e))

    # print(title_final_score)
    snippet_final_score = 0
    try:
        for j in range(len(lst) - 1):
            tmp_snippet_score = 0
            snippet = lst[j]['snippet']
            tokens = txtprc.normalizing(str(snippet))
            # print(tokens)
            for w in exc_list:
                if w in tokens:
                    tmp_snippet_score -= epsilon
                    # print(w)
            # print("after removing exclude words -->", tmp_snippet_score)
            if tmp_snippet_score > -epsilon:
                p2_lst = e2.lower().split(" ")
                if len(p2_lst) > 1:
                    if e1 in tokens and p2_lst[0] in tokens and p2_lst[1] in tokens:
                        tmp_snippet_score += snip_pos
                else:
                    if e1 in tokens and p2_lst[0] in tokens:
                        tmp_snippet_score += snip_pos

            # print("final ->", tmp_snippet_score)
            snippet_final_score += tmp_snippet_score
    except Exception as e:
        print(str(e))
    url_final_score = 0
    try:
        urls = lst[-1]['urls']
        for url in urls:
            if str(url).find(e1) != -1:
                url_final_score += url_pos
            elif str(url).find("twitter") != -1 or str(url).find("github") != -1 or str(url).find(
                    "linkedin") != -1 or str(url).find("youtube") != -1:
                url_final_score += url_pos - epsilon
    except:
        pass
    # print(url_final_score)
    final_score = round(((snippet_final_score + title_final_score + url_final_score) / 3), 2)
    return final_score

#loading the rss page
def loadPage(url, fileName=None):

    flag = False
    # setting the headers of request to get the latest news of rss feed
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    resp = requests.get(url, timeout=20, headers=headers)
    #print(resp)
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

def parseXML(xmlfile, entity1, entity2, score):

    tree = ET.parse(xmlfile)
    #get root element of xml file
    root = tree.getroot()
    #iterate over news items of xml file

    for item in root:
        for item in item.findall('item'):
            for child in item:
                if child.tag == 'link':
                    url = child.text
                elif child.tag == 'pubDate':
                    publish_date = child.text

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
                    "entity1": entity1,
                    "entity2": entity2,
                    "relationScore": score
                }
                #print(doc)
                newsTokens = txtprc.normalizing(doc['text'])

                if entity1 in newsTokens and entity2 in newsTokens:
                    #print(newsTokens)
                    writeToDb(doc)
                    print(url)
                    print(entity1, entity2)
                    print(publish_date)
            except Exception as e:
                print(str(e))
                pass

#write to the orresponding collection of mongodb
def writeToDb(doc):
    mng.writeOne("newsByEdge", doc)

def newsScrapper(tid, entity1, entity2, score):

    print(tid)
    s_lst = "2022/11/01".split('/')
    # defining start date
    start_date = datetime.date(int(s_lst[0]), int(s_lst[1]), int(s_lst[2]))
    #print(start_date)
    # defining end date
    f_lst = "2023/01/01".split('/')
    finish_date = datetime.date(int(f_lst[0]), int(f_lst[1]), int(f_lst[2]))
    #print(finish_date)
    # defining a list of dates within the defined range
    BASE_URL = 'https://news.google.com/rss'
    query = 'allintext: "{e1}" "{e2}"'.format(e1=entity1, e2=entity2) + ' '+'source: -coindesk' + ' ' + 'after:{}'.format(start_date) + ' ' + 'before:{}'.format(finish_date)
    print(query)
    URL = BASE_URL + '/search?q={}'.format(query)
    filename = 'edge12/{e1}_{e2}_news.xml'.format(e1=entity1, e2=entity2)
    flag = loadPage(URL, filename)
    if flag:
        print('successfully done')
        parseXML(filename, entity1, entity2, score)


#'source: -coindesk -cryptonaute -bitcoinist -insidebitcoins' +

#calling main to collect latest news of the feed web page
if __name__ == "__main__":
    df = mng.returnColAsDf(collection_name)
    entity_list = []
    for counter in range(df.shape[0]):
        dic = {}
        e1 = df.iloc[counter]['player']
        e2 = df.iloc[counter]['entity']
        linkStatus = df.iloc[counter]['linkStatus']
        dic['e1'] = e1
        dic['e2'] = e2
        dic['score'] = computeScore(e1, e2, linkStatus)
        entity_list.append(dic)
    #print(entity_list)
    final_list = ([e for e in entity_list if e['score'] > 0])
    num_entity = len(final_list)
    batch_size = 5
    res = num_entity % batch_size
    print(res)
    phases = int(num_entity / batch_size)
    print(phases)
    for counter in range(phases):
        can_list = final_list[counter*batch_size:(counter+1)*batch_size]
        print("current list is:", can_list)
        threads = []
        for i in range(len(can_list)):
            #print(can_list[i])
            dic = can_list[i]
            threads.append(threading.Thread(target=newsScrapper, args=(i, dic['e1'], dic['e2'], dic['score'])))
            threads[i].start()
        for j in range(len(can_list)):
            threads[j].join()
        print("counter is:", counter)
        print("waiting...")
        time.sleep(1)
    if res != 0:
        can_list = entity_list[-res:]
        threads = []
        for i in range(len(can_list)):
            threads.append(threading.Thread(target=newsScrapper, args=(i, dic['e1'], dic['e2'], dic['score'])))
            threads[i].start()
        for j in range(len(can_list)):
            threads[j].join()