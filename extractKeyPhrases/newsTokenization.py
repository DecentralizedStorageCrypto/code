from extractKeyPhrases.preprocessing import textProcessing
from db import mongodb
localhost = "mongodb://127.0.0.1:27017"
db_name = "news"
mng = mongodb(localhost, db_name)

def tokenization():
    df = mng.returnColAsDf("targetCoins")
    df['content'] = df['title'] + df['text']
    for counter in range(df.shape[0]):
        txtprc = textProcessing()
        _id = df['_id'][counter]
        news = df['content'].iloc[counter]
        tmp1 = txtprc.removeNoise(news)
        #tmp2 = txtprc.spellChecker(tmp1)
        tmp2 = txtprc.normalizing(tmp1)
        finalDoc = txtprc.removeStopWords(tmp2)
        #finalDoc = txtprc.stemming(tmp3)
        #finalDoc = txtprc.lemmatization(tmp3)
        #finalDoc = txtprc.removeNonEnglish(tmp6)
        mng.addTokenizedTextbyId("targetCoins", _id, finalDoc)

if __name__=="__main__":
    tokenization()