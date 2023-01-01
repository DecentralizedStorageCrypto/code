from db import mongodb
import pandas as pd
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup
import math
import sys

localhost = "mongodb://127.0.0.1:27017"
db_name = "players"

myclient = MongoClient(localhost)
mydb = myclient[db_name]
collectin_name = mydb["relationsV1"]

mng = mongodb(localhost, db_name)

def extractScore():

    df = pd.read_csv("allPly.csv", encoding='ANSI')

    for c1 in range(58, df.shape[0]):
        player = df.iloc[c1]['player']
        print(player)
        imp = findImp(player)
        print(player, "-->", imp)
        for c2 in range(df.shape[0]):
            dic = {}
            term2 = df.iloc[c2]['player']
            if player != term2:
                try:
                    score = computeScore(player, term2)
                except:
                    score = 0
                    pass
                print(score)
                dic['player'] = player
                dic['entity'] = term2
                dic['linkScore'] = score
                dic['repu'] = imp
                collectin_name.insert_one(dic)

def findImp(player):

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"}

    URL = "https://www.google.com/search?q=allintitle:{t1}".format(t1=player)

    result = requests.get(URL, headers=headers)

    soup = BeautifulSoup(result.content, 'html.parser')

    total_results_text = soup.find("div", {"id": "result-stats"}).find(text=True, recursive=False)
    result_num = ''.join([num for num in total_results_text if num.isdigit()])

    try:
        score = (int(result_num))
    except:
        score = 0

    return score

def computeScore(term1, term2):
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"}

    URL = "https://www.google.com/search?q=allintitle:{t1} {t2}".format(t1=term1, t2=term2)

    result = requests.get(URL, headers=headers)

    soup = BeautifulSoup(result.content, 'html.parser')

    total_results_text = soup.find("div", {"id": "result-stats"}).find(text=True, recursive=False)
    result_num = ''.join([num for num in total_results_text if num.isdigit()])

    try:
        score2 = (int(result_num))
    except:
        score2 = 0

    return score2

if __name__ == "__main__":
    extractScore()
