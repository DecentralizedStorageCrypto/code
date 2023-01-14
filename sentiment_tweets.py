import torch
import json
from transformers import T5Tokenizer, T5ForConditionalGeneration,T5Config
from transformers import BertTokenizer, BertForSequenceClassification
import numpy as np
from db import mongodb


model = T5ForConditionalGeneration.from_pretrained('t5-large')
tokenizer = T5Tokenizer.from_pretrained('t5-large')
device = torch.device('cpu')
localhost = "mongodb://127.0.0.1:27017"
db_name = "news"
collection_name = "filecoinNews"

mng = mongodb(localhost, db_name)

df = mng.returnColAsDf(collection_name)

for counter in range(df.shape[0]):
    text = str(df.iloc[counter]['tokenizedTweet'])
    print(text, end="\n")
    finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone', num_labels=3)
    tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')

    input1 = tokenizer(text, return_tensors="pt", padding=True)
    sent_scores_tweet = finbert(**input1)[0]

    labels = {0: 'neutral', 1: 'positive', 2: 'negative'}
    nmpy_tweet = sent_scores_tweet.detach().numpy()
    x1 = nmpy_tweet[0]
    sft_tweet = (np.exp(x1) / np.exp(x1).sum())
    print("The sentiment score of tweet is:", sft_tweet, end="\n")
    print("The sentiment of tweet is:", labels[np.argmax(sft_tweet)], end="\n\n")