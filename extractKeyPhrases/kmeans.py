from db import mongodb
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer, util


#initialize mongo db
localhost = "mongodb://127.0.0.1:27017"
db_name = "socialMedia"
mng = mongodb(localhost, db_name)
collectionName = "targetCoinsTfidfKeyphrases"
df = mng.returnColAsDf(collectionName)
data = df[['_id', 'keyPhrase', 'score', 'bertEmbedding', 'clusterInfo']]
#'bertEmbedding', 'clusterInfo'

dic1 = {}
dic2 = {}
for counter in range(len(data)):
    score = data.iloc[counter]['score']
    sentence = data.iloc[counter]['keyPhrase']
    if data.iloc[counter]['clusterInfo'] == 0:
        dic1[sentence] = score
    elif data.iloc[counter]['clusterInfo'] == 1:
         dic2[sentence] = score

dic1 = {k: v for k, v in sorted(dic1.items(), key=lambda item: item[1], reverse=True)}
dic2 = {k: v for k, v in sorted(dic2.items(), key=lambda item: item[1], reverse=True)}

print(dic2.items())


model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
def embedding():
    for i in range(len(data)):
        print(i)
        id = data.iloc[i]['_id']
        sentence = data.iloc[i]['keyPhrase']
        emb = model.encode(sentence, convert_to_numpy=True)
        mng.addEmbedding(collectionName, id, str(emb))

#clustering key phrases using k-means method
def clusterKeyPhrases():
    lst = []
    for i in range(len(data)):
        arr = np.fromstring(data.iloc[i]['bertEmbedding'].strip('[]'), dtype=np.float64, sep=' ')
        lst.append(arr)
    df1 = pd.DataFrame(np.array(lst))
    km = KMeans(max_iter=600, n_clusters=2).fit(df1)
    clusterIds = km.labels_
    for counter in range(len(data)):
        id = data.iloc[counter]['_id']
        cInfo = clusterIds[counter]
        mng.addClusterInfo(collectionName, id, int(cInfo))
#
if __name__ == "__main__":
    clusterKeyPhrases()
    embedding()