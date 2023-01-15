import preprocessor as prc
from db import mongodb
import re
from preprocessing import textProcessing
from bson.objectid import ObjectId
import pandas as pd
import threading

#initializing mongodb
localhost = "mongodb://127.0.0.1:27017"
db_name = "filecoinNews"
mng = mongodb(localhost, db_name)
collectionName = "tweets"
tpc = textProcessing()
prc.set_options(prc.OPT.URL, prc.OPT.MENTION, prc.OPT.RESERVED, prc.OPT.EMOJI, prc.OPT.SMILEY, prc.OPT.NUMBER )

def tweetPreProcess():
    # getting the related collection as a pandas dataframe
    data = mng.returnCorsur(collectionName)
    for counter in range(len(data)):
        _id = data[counter]['_id']
        try:
            tweet = data[counter]['text']
            print(counter)
            removeNoise = prc.clean(tweet)
            removeNumbers = tpc.removeNoise(removeNoise)
            #remove hashtag sign
            editedTweet = ' '.join(re.sub("([^0-9A-Za-z \t])", " ", removeNumbers).split())
            # normalizedtweet = tpc.normalizing(editedTweet)
            # tokenizedTweet = tpc.removeStopWords(normalizedtweet)
        except:
            editedTweet = 'unknown'

        print(editedTweet)
        mng.addTokenizedTweet(collectionName, _id, str(editedTweet))

#calling tweetPreProcess method
if __name__ == "__main__":
    tweetPreProcess()