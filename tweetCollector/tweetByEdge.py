from db import mongodb
import twint
from twint import Config
import threading
import json
import datetime
import pandas as pd
import time
import os
from preprocessing import textProcessing


parent_dir = r"C:\Users\Administrator\PycharmProjects\pythonProject\B4"
localhost = "mongodb://127.0.0.1:27017"
db_name = "players"
mng = mongodb(localhost, db_name)
collection_name = "relations"
txtprc = textProcessing()

def computeScore(e1, e2, linkStatus):
    df_exc = mng.returnColAsDf("excludeWords")
    exc_list = df_exc['word'].to_list()
    epsilon = 0.2
    title_pos = 1.5
    snip_pos = 1
    url_pos = 0.5
    null = None
    lst = (list(eval((linkStatus))))
    title_final_score = 0
    try:
        for j in range(len(lst) - 1):
            tmp_title_score = 0
            title = lst[j]['title']
            tokens = txtprc.normalizing(title)
            # print(tokens)
            for w in exc_list:
                if w in tokens:
                    tmp_title_score -= epsilon
                    # print(w)
            # print("after removing exclude words -->", tmp_title_score)
            if tmp_title_score > -epsilon:
                p2_lst = e2.lower().split(" ")
                # print(p2_lst)
                if len(p2_lst) > 1:
                    if e1 in tokens and p2_lst[0] in tokens and p2_lst[1] in tokens:
                        tmp_title_score += title_pos
                else:
                    if e1 in tokens and p2_lst[0] in tokens:
                        tmp_title_score += title_pos
            # print("final ->", tmp_title_score)
            title_final_score += tmp_title_score
    except Exception as e:
        print(str(e))

    # print(title_final_score)
    snippet_final_score = 0
    try:
        for j in range(len(lst) - 1):
            tmp_snippet_score = 0
            snippet = lst[j]['snippet']
            tokens = txtprc.normalizing(str(snippet))
            # print(tokens)
            for w in exc_list:
                if w in tokens:
                    tmp_snippet_score -= epsilon
                    # print(w)
            # print("after removing exclude words -->", tmp_snippet_score)
            if tmp_snippet_score > -epsilon:
                p2_lst = e2.lower().split(" ")
                if len(p2_lst) > 1:
                    if e1 in tokens and p2_lst[0] in tokens and p2_lst[1] in tokens:
                        tmp_snippet_score += snip_pos
                else:
                    if e1 in tokens and p2_lst[0] in tokens:
                        tmp_snippet_score += snip_pos

            # print("final ->", tmp_snippet_score)
            snippet_final_score += tmp_snippet_score
    except Exception as e:
        print(str(e))
    url_final_score = 0
    try:
        urls = lst[-1]['urls']
        for url in urls:
            if str(url).find(e1) != -1:
                url_final_score += url_pos
            elif str(url).find("twitter") != -1 or str(url).find("github") != -1 or str(url).find(
                    "linkedin") != -1 or str(url).find("youtube") != -1:
                url_final_score += url_pos - epsilon
    except:
        pass
    # print(url_final_score)
    final_score = round(((snippet_final_score + title_final_score + url_final_score) / 3), 2)
    return final_score


#keyword = "filecoin"
def collectTweet(e1, e2, date_list, delta, path):

    for date in date_list[::30]:
        c = twint.Config()
        c.Search = "{} {}".format(e1, e2)
        c.Since = date.strftime('%Y-%m-%d')
        c.Until = (date + delta).strftime('%Y-%m-%d')
        c.Lang = "en"
        c.Store_json = True
        c.Output = "{}/{}.json".format(path, e1+"_"+e2)
        twint.run.Search(c)

if __name__=="__main__":

    s_lst = "2022/12/01".split('/')
    print(s_lst)
    start_date = datetime.date(int(s_lst[0]), int(s_lst[1]), int(s_lst[2]))
    f_lst = "2023/01/01".split('/')
    finish_date = datetime.date(int(f_lst[0]), int(f_lst[1]), int(f_lst[2]))
    delta = datetime.timedelta(days=30)
    date_list = pd.date_range(start_date, finish_date).tolist()
    df = mng.returnColAsDf(collection_name)
    entity_list = []
    for counter in range(df.shape[0]):
        dic = {}
        e1 = df.iloc[counter]['player']
        e2 = df.iloc[counter]['entity']
        linkStatus = df.iloc[counter]['linkStatus']
        dic['e1'] = e1
        dic['e2'] = e2
        dic['score'] = computeScore(e1, e2, linkStatus)
        entity_list.append(dic)
    # print(entity_list)
    final_list = ([e for e in entity_list if e['score'] > 1])
    num_entity = len(final_list)
    print(num_entity)
    batch_size = 10
    res = num_entity % batch_size
    print(res)
    phases = int(num_entity / batch_size)
    print(phases)

    for counter in range(1, phases):
        directory = "tweets_{}".format(str(counter))
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        can_list = final_list[counter * batch_size:(counter + 1) * batch_size]
        p_list = [dic['e1']+"_"+dic['e2'] for dic in can_list]

        print("current list is:", can_list)
        threads = []
        for i in range(len(can_list)):
            # print(can_list[i])
            threads.append(threading.Thread(target=collectTweet, args=(can_list[i]['e1'], can_list[i]['e2'], date_list, delta, str(path))))
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
                        lst = p_list[c].split("_")
                        doc['entity1'] = lst[0]
                        doc['entity2'] = lst[1]
                        mng.writeOne("tweetByEdge", doc)
            except Exception as e:
                print(str(e))
                pass
        print("counter is:", counter)
        print("waiting...")
        time.sleep(5)
    if res != 0:
        directory = "tweets_{}".format(str(phases))
        path = os.path.join(parent_dir, directory)
        os.mkdir(path)
        can_list = final_list[-res:]
        p_list = [dic['e1']+"_"+dic['e2'] for dic in can_list]
        print("current list is:", can_list)
        threads = []
        for i in range(len(can_list)):
            threads.append(threading.Thread(target=collectTweet, args=(can_list[i]['e1'], can_list[i]['e2'], date_list, delta, str(path))))
            threads[i].start()
        for j in range(len(can_list)):
            threads[j].join()
        os.chdir(path)
        num = len([name for name in os.listdir(path)])
        try:
            with open('{}.json'.format(p_list[c]), encoding="utf8") as data:
                for jsonObj in data:
                    doc = json.loads(jsonObj)
                    lst = p_list[c].split("_")
                    doc['entity1'] = lst[0]
                    doc['entity2'] = lst[1]
                    mng.writeOne("tweetByEdge", doc)
        except Exception as e:
            print(str(e))
            pass
