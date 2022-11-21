import pandas as pd
from pygooglenews import GoogleNews
import datetime
import newspaper
from newspaper import Config
from pymongo import MongoClient
import threading
import argparse
import sys

config = Config()
config.request_timeout = 100


# collecting news articles by keyword and store it to the defined collelction of mongodb
def collectNews(tid, gn, keyword, collection_name, delta, date_list):
    try:
        # iterate over defined time frame for collecting news articles
        for date in date_list[:-1]:

            tmp = str(date).split(' ')
            startDate = tmp[0]
            endDate = (date + delta)
            tmp = str(endDate).split(' ')
            endDate = tmp[0]
            # collecing related links of news articles due to defined keyword for a specific day, using pygooglenews
            result = gn.search(keyword, helper=True, from_=startDate, to_=endDate)

            if len(result['entries']) == 0:
                sys.exit("IP was blocked by google, please try again, later !!!")

            # iterate over the collected links and collecting the news title, news body, news published date and news top image link
            for e in result['entries']:
                try:
                    print(e)
                    url = e['links'][0]['href']
                    # print(url)
                    news = newspaper.Article(url=url, language='en')
                    news.download()
                    news.parse()
                    # print(news.publish_date)
                    p_date = news.publish_date
                    if p_date == None:
                        p_date = date
                    # store the collected news as a json object
                    news = {
                        # title : News Headline
                        # text : News content
                        # authors : authors of news
                        # published_date : news timestamp
                        # top_image : related url of top image using in news
                        # link : related url
                        "title": str(news.title),
                        "text": str(news.text),
                        "authors": news.authors,
                        "published_date": p_date,
                        "top_image": str(news.top_image),
                        "link": url,
                        "keyword": keyword
                    }
                    print("from thread number", tid, "->", news)
                    # write the related json object to the corresponding collection of mongodb
                    writeToDb(news, collection_name)

                except:
                    print("unable to download news: ", url)
                    pass
    except:
        print("sorry, owing to connection issues, as of present we are not able to complete your request")
        pass


# write the collected news article to mongodb.
def writeToDb(news, collection_name):
    collection = db[collection_name]
    collection.insert_one(news)


# calling main function
if __name__ == "__main__":

    # initiating the pygooglenews instance for collecting the related links of news articles
    gn = GoogleNews(lang='en')
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input File Name")
    args = parser.parse_args()
    metadata = pd.read_csv(args.input)
    db_url = metadata.iloc[0]['db_url']
    # connecting to the mongodb
    client = MongoClient(db_url)
    db_name = metadata.iloc[0]['db_name']
    # defining database name
    db = client[db_name]
    collection_name = metadata.iloc[0]['collection_name']
    # defining the start date as well as finish date for collecting news articles
    s_lst = metadata.iloc[0]['start_date'].split(',')
    # defining start date
    start_date = datetime.date(int(s_lst[0]), int(s_lst[1]), int(s_lst[2]))
    # defining end date
    f_lst = metadata.iloc[0]['end_date'].split(',')
    finish_date = datetime.date(int(f_lst[0]), int(f_lst[1]), int(f_lst[2]))
    delta = datetime.timedelta(days=1)
    # defining a list of dates within the defined range
    date_list = pd.date_range(start_date, finish_date).tolist()
    print(date_list)
    # defining key phrases
    keyPhrases = metadata['key_phrases']
    # initializing threads
    threads = []
    for i in range(len(keyPhrases)):
        threads.append(
            threading.Thread(target=collectNews, args=(i, gn, keyPhrases[i], collection_name, delta, date_list)))
        threads[i].start()