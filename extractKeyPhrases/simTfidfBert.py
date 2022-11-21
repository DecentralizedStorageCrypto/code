from sentence_transformers import SentenceTransformer, util
import pandas as pd
import numpy as np
import csv
import ast
import threading

# localhost = "mongodb://127.0.0.1:27017"
# db_name = "news"
# mng = mongodb(localhost, db_name)
#df1 = mng.returnColAsDf("cryptocurrencyKeybert")

def calSim(tid, start,end):

    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    df1 = pd.read_csv("Data1/cryptocurrencyKeybert.csv")
    kbertSen = ast.literal_eval(str(df1.iloc[0]['highScorePhrases']))

    # df2 = mng.returnColAsDf("NgramCrypto")
    df2 = pd.read_csv("Data1/NgramCrypto.csv")
    tfIdfNgramMain = ast.literal_eval(str(df2.iloc[5]['fourNgramMain']))
    tfIdfShuffle = ast.literal_eval(str(df2.iloc[4]['fourNgramShuffle']))

    for counter in range(start, end):
        dct = {}
        sentence1 = kbertSen[counter]
        tmp = []
        for sentence2 in tfIdfNgramMain:
            sentence2 = " ".join(sentence2)
            e1 = model.encode(sentence1, convert_to_numpy=True)
            e2 = model.encode(sentence2, convert_to_numpy=True)
            cosin = float(util.cos_sim(e1, e2))
            tmp.append(cosin)

        for sentence3 in tfIdfShuffle:
            sentence3 = " ".join(sentence3)
            e1 = model.encode(sentence1, convert_to_numpy=True)
            e2 = model.encode(sentence3, convert_to_numpy=True)
            cosin = float(util.cos_sim(e1, e2))
            tmp.append(cosin)

        cosinScores = np.array(tmp)
        meanScore = np.mean(cosinScores)
        dct[sentence1] = meanScore
        #print(tid,sentence1,"--->", meanScore)
        write2csv(dct, tid)

def write2csv(dct, tid):
    with open('Result1/score-{name}.csv'.format(name=tid), 'a+', newline='') as output:
        writer = csv.writer(output)
        writer.writerows(dct.items())

if __name__=="__main__":
    threads = []
    for i in range(12):
        threads.append(threading.Thread(target=calSim, args=(i, (i*100), (i+1)*100)))
        threads[i].start()
