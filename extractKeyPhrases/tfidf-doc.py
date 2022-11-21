from db import mongodb
import pandas as pd
import numpy as np
from nltk.util import ngrams
from random import shuffle
from sentence_transformers import SentenceTransformer, util
import re
from numpy.linalg import norm

#initialize mongo db and load data
localhost = "mongodb://127.0.0.1:27017"
db_name = "socialMedia"
mng = mongodb(localhost, db_name)
collectionName = "storageKeywords"
df1 = mng.returnSelectedColAsDf("storage")
data1 = df1['bertEmbedding']
arr = np.fromstring(data1[0].strip('[]'), dtype=np.float64, sep=' ')
df2 = mng.returnColAsDf(collectionName)
data2 = pd.DataFrame(list(df2))
#shuffling the tf-idf keywords forming the n-gram with 2,3 and 4 lenghts
words = list(df2.columns)[1:100]
shuffle(words)
fourGrams = ngrams(words, 2)
result = list(fourGrams)
#initialize all-mpnet-base-v2 model
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
#computing the similarity between embedding of news documents and tf-idf n-grams
def calSim():
    for i in range(len(result)):
        tmp = list(result[i])
        print(tmp)
        text = ",".join(result[i])
        sentence1 = re.sub(',', ' ', text)
        print(sentence1)
        e1 = model.encode(sentence1, convert_to_numpy=True)
        tmp = []
        for j in range(len(data1)):
            e2 = np.fromstring(data1[j].strip('[]'), dtype=np.float64, sep=' ')
            cosin = np.dot(e1, e2) / (norm(e1) * norm(e2))
            tmp.append(cosin)
        arr = np.array(tmp)
        average = np.mean(arr)
        output = {'keyPhrase': sentence1, 'score': average}
        mng.writeOne("storageTfidfKeyphrases", output)

if __name__ == "__main__":
    calSim()


