from db import mongodb
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import time
import numpy as np
from transformers import BertTokenizer
from pymongo import MongoClient
import enchant
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import math

localhost = "mongodb://127.0.0.1:27017"
db_name = "arweaveNews"
mng = mongodb(localhost, db_name)

myclient = MongoClient(localhost)
mydb = myclient[db_name]
collectin_name = mydb["candidatePlayers"]

def findUnkownByEnchant():

    df = mng.returnColAsDf("news")
    docList =[]
    tmp = []
    for counter in range(df.shape[0]):
        print(counter)
        lst = df.iloc[counter]['KeyPhrase']
        for dic in lst:
            doc = dic['phrase']
            docList.append(doc)

    vectorizer = CountVectorizer(stop_words='english')
    vectorizer.fit(docList)
    allTokens = list(vectorizer.vocabulary_.keys())
    for token in allTokens:
        d = enchant.Dict("en_US")
        a = d.check(token)
        if a == False:
            tmp.append(token)
    df = pd.DataFrame(tmp)
    df.to_csv("players/arweaveNews.csv")

def findUnknownbyBert(token):

    flag = False
    tz = BertTokenizer.from_pretrained("bert-base-cased")
    lst = tz.convert_tokens_to_ids([token])
    if lst[0] == 100:
        flag = True
    return flag


def scorePlayers():

    df = pd.read_csv("players/arweaveNews.csv")
    df.columns = ['index', 'candidate']
    for counter in range(df.shape[0]):
        token = df.iloc[counter]['candidate']
        dic = {}
        print(token)
        dic['candidate player'] = token
        s1, s2 = computeScore(token)
        dic['score1'] = s1
        dic['score2'] = s2
        collectin_name.insert_one(dic)

def computeScore(token):

    score1 = 0
    score2 = 0
    query = token

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"}
    URL = "https://www.google.com/search?q= {term}".format(term=token)
    result = requests.get(URL, headers=headers)
    soup = BeautifulSoup(result.content, 'html.parser')
    anchors = soup.find(id='search').findAll('a')
    for a in anchors:
        try:
            link = str(a['href'])
            if link.startswith("https"):
                domain = urlparse(link).netloc
                lst = domain.split(".")
                editedDomain = " ".join(lst[:-1])
                #print(editedDomain)

                if editedDomain.find(token) != -1:
                    score1 += 3

                if editedDomain.find("wikipedia") != -1:
                    score1 += 1

                if editedDomain.find("linkedin") != -1:
                    score1 += 1

                if editedDomain.find("twitter") != -1:
                    score1 += 2

                if editedDomain.find("github") != -1:
                    score1 += 2

                if editedDomain.find("instagram") != -1:
                    score1 += 1

                if editedDomain.find("facebook") != -1:
                    score1 += 1

                if editedDomain.find("wallex") != -1:
                    score1 += 1

                if editedDomain.find("forbes") != -1:
                    score1 += 1

                if editedDomain.find("binance") != -1:
                    score1 += 1

                if editedDomain.find("coindesk") != -1:
                    score1 += 1

                if editedDomain.find("cointelegraph") != -1:
                    score1 += 1

                if editedDomain.find("crypto") != -1:
                    score1 += 1

                if editedDomain.find("cnbc") != -1:
                    score1 += 1

                if editedDomain.find("reddit") != -1:
                    score1 += 1

                if editedDomain.find("youtube") != -1:
                    score1 += 1
        except:
            continue

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"}

    URL = "https://www.google.com/search?q= allintext:{candidateToken} siacoin".format(candidateToken=token)

    result = requests.get(URL, headers=headers)

    soup = BeautifulSoup(result.content, 'html.parser')

    try:
        total_results_text = soup.find("div", {"id": "result-stats"}).find(text=True, recursive=False)
        result_num = ''.join([num for num in total_results_text if num.isdigit()])
        score2 = math.log10(int(result_num))
    except:
        score2 = 0
    return score1, score2

def addAggrScore():

    df = mng.returnColAsDf("siacoinPlayers")
    tmp1 = []
    tmp2 = []
    for counter in range(df.shape[0]):
        score1 = df['score1'][counter]
        score2 = df['score2'][counter]
        tmp1.append(score1)
        tmp2.append(score2)
    arr1 = np.array(tmp1)
    arr2 = np.array(tmp2)
    normalized_x = (arr1 - np.min(arr1)) / (np.max(arr1) - np.min(arr1)) * 10
    finalScore = normalized_x * arr2
    for i in range(len(df)):
        _id = df['_id'][i]
        score = finalScore[i]
        print(score)
        mng.addAggScore("siacoinPlayers", _id, score)


if __name__ =="__main__":

    findUnkownByEnchant()
    scorePlayers()
    addAggrScore()