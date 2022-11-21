from db import mongodb
import numpy as np
from sentence_transformers import SentenceTransformer
from numpy.linalg import norm

#initialize mongo db and loading data
localhost = "mongodb://127.0.0.1:27017"
db_name = "socialMedia"
mng = mongodb(localhost, db_name)
collectionName = "targetCoinsKeybert"
df1 = mng.returnSelectedColAsDf("targetCoins")
data1 = df1['bertEmbedding']
arr = np.fromstring(data1[0].strip('[]'), dtype=np.float64, sep=' ')
df2 = mng.returnColAsDf(collectionName)
data2 = df2.iloc[0]['highScorePhrases']
#initialize all-mpnet-base-v2 model
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
#computing the similarity between embedding of news documents and tf-idf n-grams
def calSim():
    for sentence1 in data2:
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
        mng.writeOne("targetCoinsKeyBertKeyphrases", output)

if __name__ == "__main__":
    calSim()


