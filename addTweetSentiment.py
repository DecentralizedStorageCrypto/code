import torch
import json
from transformers import BertTokenizer, BertForSequenceClassification
import numpy as np
from db import mongodb
import threading

device = torch.device('cpu')
localhost = "mongodb://127.0.0.1:27017"
db_name = "players"
collection_name = "tweetByNode"

mng = mongodb(localhost, db_name)

def addSnt(start, end):

    for counter in range(start, end):
        try:
            _id = df['_id'][counter]
            tokenizedText = str(df.iloc[counter]['tokenizedTweet'])
            lst = (list(eval(tokenizedText)))
            tweetText = ' '.join(lst)
            finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone', num_labels=3)
            tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')
            input1 = tokenizer(tweetText, return_tensors="pt", padding=True)
            sent_scores_tweet = finbert(**input1)[0]
            labels = {0: 'neutral', 1: 'positive', 2: 'negative'}
            nmpy_tweet = sent_scores_tweet.detach().numpy()
            x1 = nmpy_tweet[0]
            sft_tweet = (np.exp(x1) / np.exp(x1).sum())
            print("The sentiment score of tweet is:", sft_tweet, end="\n")
            print("The sentiment of tweet is:", labels[np.argmax(sft_tweet)], end="\n\n")
            mng.addAggSentimentScore(collection_name, _id, str(sft_tweet))
            mng.addAggSentimentLabel(collection_name, _id, str(labels[np.argmax(sft_tweet)]))

        except Exception as e:
            print(str(e))
            pass

#initialize the main fnction
if __name__ == "__main__":

    df = mng.returnColAsDf(collection_name)
#batch size determines, number of sentences that assigns to each thread.
    batch_size = 1000
#total size, determines total number of news articles for summary etraction and sentiment analysis.
    total = 120000
#base determines the starting point of news articles.
    base = 90000
    counter = int(total/batch_size)
    threads = []
    for i in range(counter):
        threads.append(threading.Thread(target=addSnt, args=((i*batch_size)+base, ((i+1)*batch_size)+base)))
        threads[i].start()
    for j in range(counter):
        threads[j].join()