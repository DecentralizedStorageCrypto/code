from db import mongodb
import twint
from twint import Config
import threading
import json
import datetime
import pandas as pd
import time
import os

parent_dir = r"C:\Users\Administrator\PycharmProjects\pythonProject\A12"
localhost = "mongodb://127.0.0.1:27017"
db_name = "players"
mng = mongodb(localhost, db_name)
collection_name = "entities"

#keyword = "filecoin"
def collectTweet(player, twitterAccount, date_list, delta, path):

    for date in date_list[::10]:
        c = twint.Config()
        c.Username = twitterAccount
        c.Since = date.strftime('%Y-%m-%d')
        c.Until = (date + delta).strftime('%Y-%m-%d')
        c.Lang = "en"
        c.Store_json = True
        c.Output = "{}/{}.json".format(path, player)
        twint.run.Search(c)

if __name__=="__main__":

    s_lst = "2022/12/01".split('/')
    print(s_lst)
    start_date = datetime.date(int(s_lst[0]), int(s_lst[1]), int(s_lst[2]))
    f_lst = "2023/01/01".split('/')
    finish_date = datetime.date(int(f_lst[0]), int(f_lst[1]), int(f_lst[2]))
    delta = datetime.timedelta(days=10)
    date_list = pd.date_range(start_date, finish_date).tolist()
    #print(date_list)

    df = mng.returnColAsDf(collection_name)
    entity_list = []
    player_list = []
    for counter in range(df.shape[0]):
        if df.iloc[counter]['twitter'] != ' ':
            entity_list.append(df.iloc[counter]['twitter'])
            player_list.append(df.iloc[counter]['player'])
    num_entity = len(entity_list)
    batch_size = 10
    res = num_entity % batch_size
    print(res)
    phases = int(num_entity / batch_size)
    print(phases)
    for counter in range(phases):
        directory = "tweets_{}".format(str(counter))
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        can_list = entity_list[counter * batch_size:(counter + 1) * batch_size]
        p_list = player_list[counter * batch_size:(counter + 1) * batch_size]
        print("current list is:", can_list)
        threads = []
        for i in range(len(can_list)):
            # print(can_list[i])
            threads.append(threading.Thread(target=collectTweet, args=(p_list[i], can_list[i], date_list, delta, str(path))))
            threads[i].start()
        for j in range(len(can_list)):
            threads[j].join()
        os.chdir(path)
        num = len([name for name in os.listdir(path)])
        for c in range(num):
            try:
                with open('{}.json'.format(p_list[c]), encoding="utf8") as data:
                    for jsonObj in data:
                        doc = json.loads(jsonObj)
                        doc['entity'] = p_list[c]
                        mng.writeOne("tweetByNode2", doc)
            except:
                pass
        print("counter is:", counter)
        print("waiting...")
        time.sleep(2)
    if res != 0:
        directory = "tweets_{}".format(str(phases))
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        can_list = entity_list[-res:]
        p_list = player_list[-res:]
        print("current list is:", can_list)
        threads = []
        for i in range(len(can_list)):
            threads.append(threading.Thread(target=collectTweet, args=(p_list[i], can_list[i], date_list, delta, str(path))))
            threads[i].start()
        for j in range(len(can_list)):
            threads[j].join()
        os.chdir(path)
        num = len([name for name in os.listdir(path)])
        try:
            with open('{}.json'.format(p_list[c]), encoding="utf8") as data:
                for jsonObj in data:
                    doc = json.loads(jsonObj)
                    doc['entity'] = p_list[c]
                    mng.writeOne("tweetByNode2", doc)
        except:
            pass