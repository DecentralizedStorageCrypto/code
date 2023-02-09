from db import mongodb
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse


def extractLinks():

    df = mng.returnColAsDf(collection_name_1)
    candidate_list = ['filecoin', 'storj', 'siacoin', 'arweave']
    for c1 in candidate_list:
        player = c1
        print(player)
        for c2 in range(df.shape[0]):
            dic = {}
            term2 = df.iloc[c2]['player']
            if player != term2:
                print(term2)
                dic['player'] = player
                dic['entity'] = term2
                lst_doc = collectData(player, term2)
                dic['linkStatus'] = lst_doc
                #mng.writeOne(collection_name_2, dic)

def collectData(term1, term2):

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

    metadata = pd.read_csv('metadata.csv')
    dbUrl = metadata.iloc[0]['db_url']
    db_name = metadata.iloc[0]['db_name']
    mng = mongodb(dbUrl, db_name)
    collectin_name_1 = metadata.iloc[0]['collectin_name1']
    collectin_name_2 = metadata.iloc[0]['collectin_name2']
    extractLinks()
