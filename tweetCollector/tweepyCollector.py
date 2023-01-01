import tweepy
from db import mongodb
import pandas as pd


localhost = "mongodb://127.0.0.1:27017"
db_name = "persons"
mng = mongodb(localhost, db_name)
#Keys
consumer_key = "O40hztalTNp3NGoyrgXcoMJ4r"
consumer_secret = "1Kbw8Rh5zablSy081e8rcumcGTAVGNHHz0UGgV8pTkmbhg6LOr"
access_token = "835610467213185024-zt0KuZKMi7G9RKorRVbNrWHRIduUUjr"
access_token_secret = "1SZdp9Sj9oSqcucWQRsDSpfXMOEWsuZblHzSkOw4RqJhc"

def writeOneToDb(doc,collection_name):
    mng = mongodb(localhost, db_name)
    mng.writeOne(collection_name, doc)

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

name = "samecwilliams"

tweets = api.user_timeline(screen_name=name,
                           # 200 is the maximum allowed count
                           count=200,
                           include_rts = False,
                           # Necessary to keep full_text
                           # otherwise only the first 140 words are extracted
                           tweet_mode = 'extended'
                           )


all_tweets = []
all_tweets.extend(tweets)
oldest_id = tweets[-1].id

while True:
    tweets = api.user_timeline(screen_name=name,
                           # 200 is the maximum allowed count
                           count=200,
                           include_rts = False,
                           max_id = oldest_id - 1,
                           # Necessary to keep full_text
                           # otherwise only the first 140 words are extracted
                           tweet_mode = 'extended'
                           )
    if len(tweets) == 0:
        break
    oldest_id = tweets[-1].id
    all_tweets.extend(tweets)
    print('N of tweets downloaded till now {}'.format(len(all_tweets)))

print(all_tweets)

outtweets = [[tweet.id_str,
              tweet.created_at,
              tweet.favorite_count,
              tweet.retweet_count,
              tweet.entities,
              tweet.full_text.encode("utf-8").decode("utf-8")]
             for idx,tweet in enumerate(all_tweets)]
df = pd.DataFrame(outtweets,columns=["id","created_at","favorite_count","retweet_count","entities", "text"])
df.to_csv('%s_tweets.csv' % name,index=False)

