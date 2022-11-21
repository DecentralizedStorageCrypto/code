from db import mongodb
import pandas as pd
import numpy as np
from collections import Counter
from extractKeyPhrases.preprocessing import textProcessing
from sklearn.feature_extraction.text import TfidfVectorizer

#initializing mongodb
localhost = "mongodb://127.0.0.1:27017"
db_name = "news"
collectionName = "targetCoins"
mng = mongodb(localhost, db_name)
#getting the related collection as a pandas dataframe
df = mng.returnColAsDf(collectionName)
#getting tokenized content in addition to tokenized header of news
tokenizedNews = df['tokenizedText'].to_list()
#implementing tf-idf method on the tokenized text of news article
vectorizer = TfidfVectorizer()
response = vectorizer.fit_transform(tokenizedNews[:8000])
df_tfidf = pd.DataFrame(response.toarray(), columns=vectorizer.get_feature_names())
#storing the obtained scores of each word related to each news article as a csv file
df_tfidf.to_csv("tfidfData/tfidf-{name}.csv".format(name=collectionName))
#extracting top 10 words with the highest tf-idf scores from each news aricle
rankWords = df_tfidf.apply(np.argsort, axis=1)
rankedWords = df_tfidf.columns.to_series()[rankWords.values[:, ::-1][:, :5]]
#storing the words with the highest tf-idf scores as a dataframe
df_result = pd.DataFrame(rankedWords)
df_result.to_csv("tfidfData/tfidf_top10-{name}.csv".format(name=collectionName))
#concatinating all collected words of news articles as a single list
keywords = df_result.values.flatten().tolist()
#removing non english words from the obtained list
prc = textProcessing()
clean_list = prc.removeNonEnglish(keywords)
#count the occurance of each word and sort the result descendingly and store it in mongodb
keywordsNum = Counter(clean_list)
keywordsNum = dict(keywordsNum)
sortedKeywords = {k: v for k, v in sorted(keywordsNum.items(), key=lambda item: item[1], reverse=True)}
mng.writeOne("{name}Keywords".format(name=collectionName), sortedKeywords)