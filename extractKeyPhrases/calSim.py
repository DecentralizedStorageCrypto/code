from sentence_transformers import SentenceTransformer, util
import pandas as pd
import numpy as np
import csv
#from db import mongodb
import ast
import threading

#computing similarity between selected key phrases and constructed n-grams of ti-idf words
def calSimilarity(tid, start,end):
    #initiating BERT model to compute embedding of key phrases as well as tf-idf n-grams
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    df1 = pd.read_csv("Data1/targetCoinsKeybert.csv")
    kbertSen = ast.literal_eval(str(df1.iloc[0]['highScorePhrases']))
    df2 = pd.read_csv("Data1/NgramtargetCoins.csv")
    tfIdfNgramMain = ast.literal_eval(str(df2.iloc[0]['fourNgramMain']))
    tfIdfShuffle = ast.literal_eval(str(df2.iloc[1]['fourNgramShuffle']))

    #computing the average score similarty between the embedding of each key phrase and n-gram of tf-idf embeddings
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
        print(dct.items())
        write2csv(dct, tid)
#write the result as csv file
def write2csv(dct, tid):

    with open('Result3/score-{name}.csv'.format(name=tid), 'a+', newline='') as output:
        writer = csv.writer(output)
        writer.writerows(dct.items())

#initiating threads and call calSimilarity method
if __name__=="__main__":
    threads = []
    for i in range(10):
        threads.append(threading.Thread(target=calSimilarity, args=(i, (i * 100), (i + 1) * 100)))
        threads[i].start()
