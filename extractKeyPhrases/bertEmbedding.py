from sentence_transformers import SentenceTransformer, util
from db import mongodb
import threading
import re
#initialize mongo db
localhost = "mongodb://127.0.0.1:27017"
db_name = "socialMedia"
mng = mongodb(localhost, db_name)
collectionName = "targetCoins"
df1 = mng.returnSelectedColAsDf(collectionName)
data = df1[['_id', 'editedTweet']]
#initialize all-mpnet-base-v2 model
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
#embedding the news articles and add the result to mongodb
def calEmbedding(tid):
        for counter in range(len(data)):
                print(tid, "-->", counter)
                id = data.iloc[counter]['_id']
                sentence = data.iloc[counter]['editedTweet']
                #tokenizedText = list(eval(data.iloc[counter]['tokenizedText']))[:512]
                # tmp = ",".join(tokenizedText)
                # sentence = re.sub(',', ' ', tmp)
                emb = model.encode(sentence, convert_to_numpy=True)
                mng.addEmbedding(collectionName, id, str(emb))
#calling threads in main to implement calEmbedding method
if __name__ == "__main__":
        calEmbedding(1)
        # threads = []
        # for i in range(10):
        #         threads.append(threading.Thread(target=calEmbedding, args=(i, (i * 1000), (i + 1) * 1000)))
        #         threads[i].start()