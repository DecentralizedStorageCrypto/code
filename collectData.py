import pandas as pd
import datetime
import newspaper
import yfinance as yf
from newspaper import Config
from pymongo import MongoClient
import threading
from db import mongodb
from datetime import date
import twint
from twint import Config
from bs4 import BeautifulSoup, SoupStrainer
import httplib2

config = Config()
config.request_timeout = 100
# collecting news articles by keyword and store it to the defined collelction of mongodb
def collectInfo(tid, keyword, date, delta, db_name, fin):

    startDate = str(date - delta)
    endDate = str(date)

    try:
        query = 'allintext:{term}'.format(term=keyword) + ' ' + 'when:1d'
        print(query)
        URL = "https://news.google.com/search?q={query}".format(query=query)
        http = httplib2.Http()
        status, response = http.request(URL)
        urls = []
        for link in BeautifulSoup(response, 'html.parser', parse_only=SoupStrainer('a')):
            if link.has_attr('href') and str(link['href']).startswith("./articles"):
                tmp = link['href']
                if tmp not in urls:
                    urls.append(tmp)
        if len(urls) > 0:
            for url in urls:
                try:
                    url = url.split('.')
                    url = "https://news.google.com" + url[1]
                    print(url)
                    news = newspaper.Article(url=url, language='en')
                    news.download()
                    news.parse()
                    p_date = news.publish_date
                    if p_date == None:
                        p_date = date
                    news = {
                        "title": str(news.title),
                        "text": str(news.text),
                        "authors": news.authors,
                        "published_date": p_date,
                        "top_image": str(news.top_image),
                        "link": url,
                        "keyword": keyword
                    }
                    print("from thread number", tid, "->", news)
                    writeOneToDb(news, db_name, "news")
                except Exception as e:
                    f = open('result.txt', 'a')
                    f.write("news --> this {url} was not downloaded.\n".format(url=url))
                    error = "Oops!" , e.__class__, "occurred.\n"
                    f.write(str(error))
                    f.close()
                    print("Oops!", e.__class__, "occurred.")
                    pass

    except Exception as e:
        f = open('result.txt', 'a')
        f.write("news --> network error was occurred, please try again\n")
        error = "Oops!", e.__class__, "occurred.\n"
        f.write(str(error))
        f.close()
        print("Oops!", e.__class__, "occurred.")
        pass
    try:
        config: Config = twint.Config()
        config.Search = keyword
        config.Lang = "en"
        config.Since = date.strftime('%Y-%m-%d')
        config.Until = (date + delta).strftime('%Y-%m-%d')
        config.Store_csv = True
        config.Output = "tweets--{db_name}--{tid}--{keyword}.csv".format(db_name=db_name, tid=tid, keyword = keyword)
        twint.run.Search(config)
    except Exception as e:
        f = open('result.txt', 'a')
        f.write("tweets --> network error was occurred, please try again\n")
        error = "Oops!", e.__class__, "occurred.\n"
        f.write(str(error))
        f.close()
        print("Oops!", e.__class__, "occurred.")
        pass
    if tid == 0:
        try:
            price_5m = yf.download(tickers=fin, start=startDate, end=endDate, interval='5m')
            price_5m['date'] = str(date)
            writeManyToDb(price_5m.to_dict('records'), db_name, 'finance_info_5m')
            price_15m = yf.download(tickers=fin, start=startDate, end=endDate, interval='15m')
            price_15m['date'] = str(date)
            writeManyToDb(price_15m.to_dict('records'), db_name, 'finance_info_15m')

            price_30m = yf.download(tickers=fin, start=startDate, end=endDate, interval='30m')
            price_30m['date'] = str(date)
            writeManyToDb(price_30m.to_dict('records'),db_name, 'finance_info_30m')

            price_60m = yf.download(tickers=fin, start=startDate, end=endDate, interval='60m')
            price_60m['date'] = str(date)
            writeManyToDb(price_60m.to_dict('records'), db_name, 'finance_info_60m')

            price_90m = yf.download(tickers=fin, start=startDate, end=endDate, interval='90m')
            price_90m['date'] = str(date)
            writeManyToDb(price_90m.to_dict('records'), db_name, 'finance_info_90m')

        except Exception as e:
            f = open('result.txt', 'a')
            f.write("financeInfo --> network error was occurred, please try again\n")
            error = "Oops!", e.__class__, "occurred.\n"
            f.write(str(error))
            f.close()
            print("Oops!", e.__class__, "occurred.")
    try:
        tweets_df = pd.read_csv("tweets--{db_name}--{tid}--{keyword}.csv".format(db_name=db_name, tid=tid, keyword=keyword))
        writeManyToDb(tweets_df.to_dict('records'), db_name, 'tweets')
    except Exception as e:
        f = open('result.txt', 'a')
        f.write("tweets --> during writing to mongodb an error was occurred, please try again\n")
        error = "Oops!", e.__class__, "occurred.\n"
        f.write(str(error))
        f.close()
        print("Oops!", e.__class__, "occurred.")

def writeOneToDb(doc,db_name, collection_name):

    mng = mongodb(localhost, db_name)
    mng.writeOne(collection_name, doc)

def writeManyToDb(docs, db_name, collection_name):

    mng = mongodb(localhost, db_name)
    mng.writMany(collection_name, docs)

if __name__ == "__main__":

    dbs = ['filecoin', 'storj', 'siacoin']
    price = ['FIL-USD', 'STORJ-USD', 'SC-USD']
    for counter in range(len(dbs)):
        localhost = "mongodb://127.0.0.1:27017"
        db_name = dbs[counter]
        fin = price[counter]
        client = MongoClient(localhost)
        # defining database name
        db = client[db_name]
        mng = mongodb(localhost, db_name)
        collection_name = "players"
        player_df = mng.returnColAsDf(collection_name)
        today = date.today()
        c_date = today.strftime("%Y,%m,%d")
        d_lst = c_date.split(',')
        date = datetime.date(int(d_lst[0]), int(d_lst[1]), int(d_lst[2]))
        delta = datetime.timedelta(days=1)
        # defining a list of dates within the defined range
        date_list = pd.date_range(date - delta, date).tolist()
        print(date_list)
        # initializing threads
        threads = []
        for i in range(player_df.shape[0]):
            phrase = player_df.iloc[i]['player']
            print(phrase)
            threads.append(threading.Thread(target=collectInfo, args=(i, phrase, date, delta, db_name, fin)))
            threads[i].start()
        for j in range(len(threads)):
            threads[j].join()



