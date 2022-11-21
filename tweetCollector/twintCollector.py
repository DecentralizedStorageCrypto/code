import twint
from twint import Config
import threading
import datetime
import pandas as pd
import argparse
from pymongo import MongoClient

#In this method using twint package the related tweets with specific keyword are collected
def tweetCollector(tid,keyword, collection_name, delta, dateList):
    for date in dateList[:-1]:
        print("Thread id is --> {id}".format(id=tid))
        print(date)
        # collect tweets related to special keyword from twitter
        config: Config = twint.Config()
        config.Search = keyword
        config.Lang = "en"
        config.Since = date.strftime('%Y-%m-%d')
        config.Until = (date + delta).strftime('%Y-%m-%d')
        config.Store_csv = True
        config.Output = "output.csv"
        twint.run.Search(config)

#convert csv to json
def convertCSVToJSON():

    with open("output.csv", 'r', encoding="utf8") as csvfile:
        fline = csvfile.readline()
        header = fline.split(",")
        data = csvfile.readlines()
        for row in data:
            row = row.split(",")
            doc = {}
            try:
                for counter in range(0, len(header)):
                    doc[header[counter]] = row[counter]
                writeToDb(doc, collection_name)
            except:
                print("something was wrong !!!")
                pass

def writeToDb(doc, collection_name):
    collection = db[collection_name]
    collection.insert_one(doc)

#calling main function
if __name__ == "__main__":

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
    s_lst = metadata.iloc[0]['start_date'].split(',')
    print(s_lst)
    #defining start date
    start_date = datetime.date(int(s_lst[0]), int(s_lst[1]), int(s_lst[2]))
    #defining end date
    f_lst = metadata.iloc[0]['end_date'].split(',')
    finish_date = datetime.date(int(f_lst[0]), int(f_lst[1]), int(f_lst[2]))
    delta = datetime.timedelta(days=1)
    # defining a list of dates within the defined range
    date_list = pd.date_range(start_date, finish_date).tolist()
    print(date_list)
    #defining key phrases
    keyPhrases = metadata['key_phrases']
    #defining multiple threrad to collect the tweets in parallel
    threads = []
    for i in range(len(keyPhrases)):
        threads.append(threading.Thread(target=tweetCollector, args=(i, keyPhrases[i],collection_name, delta, date_list)))
        threads[i].start()
    for j in range(len(threads)):
        threads[j].join()
    convertCSVToJSON()

