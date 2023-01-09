from db import mongodb
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import sys

localhost = "mongodb://127.0.0.1:27017"
db_name = "players"

localhost = "mongodb://127.0.0.1:27017"
db_name = "players"
mng = mongodb(localhost, db_name)
collectin_name_1 = "entitiesV2"
collectin_name_2 = "relationsV2"

def extractLinks():

    df = mng.returnColAsDf(collectin_name_1)
    print(df.iloc[132])

    coin_list = ['filecoin', 'storj']
    for c1 in coin_list:
        player = c1
        print(player)
        for c2 in range(132, df.shape[0]):
            dic = {}
            term2 = df.iloc[c2]['twitter']
            if player != term2:
                print(term2)
                dic['player'] = player
                dic['entity'] = term2
                lst_doc = extractData(player, term2)
                dic['linkStatus'] = str(lst_doc)
                #print(dic)
                mng.writeOne(collectin_name_2, dic)

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
