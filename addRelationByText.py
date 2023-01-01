from db import mongodb
import pandas as pd
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


localhost = "mongodb://127.0.0.1:27017"
db_name = "players"

myclient = MongoClient(localhost)
mydb = myclient[db_name]
collectin_name = mydb["relations-v33"]

mng = mongodb(localhost, db_name)

def extractLinks():

    df = pd.read_csv("allPly.csv", encoding='ANSI')
    candidate_list = ['filecoin', 'storj', 'siacoin', 'arweave']
    for c1 in range(0, 4):
        player = df.iloc[c1]['player']
        print(player)
        for c2 in range(df.shape[0]):
            dic = {}
            term2 = df.iloc[c2]['player']
            if player != term2:
                print(term2)
                dic['player'] = player
                dic['entity'] = term2
                lst_doc = extractData(player, term2)
                dic['linkStatus'] = lst_doc
                collectin_name.insert_one(dic)

def extractData(term1, term2):
    collected_data = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"}

    URL = "https://www.google.com/search?q=allintext: {t1} {t2}".format(t1=term1, t2=term2)

    html = requests.get(URL, headers=headers)

    soup = BeautifulSoup(html.text, 'lxml')
    domains = []
    anchors = soup.find(id='search').findAll('a')
    for a in anchors:
        try:
            link = str(a['href'])
            if link.startswith("https"):
                domain = urlparse(link).netloc
                lst = domain.split(".")
                editedDomain = " ".join(lst[:-1])
                domains.append(editedDomain)
        except:
            pass

    for result in soup.select(".tF2Cxc"):
        doc = {}
        try:
            title = result.select_one(".DKV0Md").text
        except:
            title = None
        try:
            snippet = result.select_one(".lEBKkf").text
        except:
             snippet = None

        doc['title'] = title
        doc['snippet'] = snippet
        collected_data.append(doc)
    doc2 = {}
    doc2['urls'] = domains
    collected_data.append(doc2)
    print("data=>", collected_data)
    return collected_data

if __name__ == "__main__":
    extractLinks()
