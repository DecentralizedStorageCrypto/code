from neoHandler import NEO4J
from db import mongodb
from preprocessing import textProcessing
import datetime
import pandas as pd

class network:

    def __init__(self, neoUrl, neoUser, neoPass):
        self.neoUrl = neoUrl
        self.neoUser = neoUser
        self.neoPass = neoPass
        self.neo = NEO4J(self.neoUrl, self.neoUser, self.neoPass)

    def removeNet(self, db_name):
        self.neo.clear_graph(db_name)

    def add_node_category(self, collection_name, db_name):
        localhost = "mongodb://127.0.0.1:27017"
        mongo_db_name = "players"
        mng = mongodb(localhost, mongo_db_name)
        df_1 = mng.returnColAsDf(collection_name)
        for counter in range(df_1.shape[0]):
            player1 = df_1.iloc[counter]['root']
            players2 = df_1.iloc[counter]['child'].split("-")
            category1 = player1.split("-")
            self.neo.create_new_player(db_name, category1, player1)
            for p2 in players2:
                #category2 = p2.split("-")
                lst_cat = category1
                self.neo.create_new_player(db_name, lst_cat, p2)

    def add_node_entity(self, collection_name_1, collection_name_2, collection_name_3, db_name):
        localhost = "mongodb://127.0.0.1:27017"
        mongo_db_name = "players"
        mng = mongodb(localhost, mongo_db_name)
        df_1 = mng.returnColAsDf(collection_name_1)
        s_lst = "2022/01/01".split('/')
        start_date = datetime.date(int(s_lst[0]), int(s_lst[1]), int(s_lst[2]))
        f_lst = "2023/01/01".split('/')
        finish_date = datetime.date(int(f_lst[0]), int(f_lst[1]), int(f_lst[2]))
        date_list = pd.date_range(start_date, finish_date).tolist()
        for counter in range(df_1.shape[0]):
            player = df_1.iloc[counter]['player']
            category = df_1.iloc[counter]['category'].split("-")
            url = str(df_1.iloc[counter]['link'])
            twitter = str(df_1.iloc[counter]['twitter'])
            description = str(df_1.iloc[counter]['description'])
            df_2 = mng.findNewsByNode(collection_name_2, date_list[-120], date_list[-1], player)
            df_3 = mng.findTweetByNode(collection_name_3, date_list[-120], date_list[-1], player)
            n_pos, n_neut, n_neg = 0, 0, 0
            t_pos, t_neut, t_neg = 0, 0, 0

            pos_titles = []
            neg_titles = []
            neut_titles = []

            for i in range(df_2.shape[0]):
                news_sent = df_2.iloc[i]['aggLabel']
                if news_sent == "positive":
                    n_pos += 1
                    tmp = "**" + str(df_2.iloc[i]['title']).replace("\"", " ")+"**"
                    pos_titles.append(tmp)
                elif news_sent == "neutral":
                    n_neut += 1
                    tmp = "**" + str(df_2.iloc[i]['title']).replace("\"", " ")+"**"
                    neut_titles.append(tmp)
                elif news_sent == "negative":
                    n_neg += 1
                    tmp = "**" + str(df_2.iloc[i]['title']).replace("\"", " ") + "**"
                    neg_titles.append(tmp)

            pos_tweets = []
            neg_tweets = []
            neut_tweets = []

            for i in range(df_3.shape[0]):
                tweet_sent = df_3.iloc[i]['aggLabel']
                if tweet_sent == "positive":
                    t_pos += 1
                    lst = list(eval((df_3.iloc[i]['tokenizedTweet'])))
                    tmp = "**"+" ".join(lst).replace("\"", " ")+"**"
                    pos_tweets.append(tmp)
                elif tweet_sent == "neutral":
                    t_neut += 1
                    lst = list(eval((df_3.iloc[i]['tokenizedTweet'])))
                    tmp = "**" + " ".join(lst).replace("\"", " ") + "**"
                    neut_tweets.append(tmp)
                elif tweet_sent == "negative":
                    t_neg += 1
                    lst = list(eval((df_3.iloc[i]['tokenizedTweet'])))
                    tmp = "**" + " ".join(lst).replace("\"", " ") + "**"
                    neg_tweets.append(tmp)

            news_pos_sent = n_pos
            news_neut_sent = n_neut
            news_neg_sent = n_neg
            tweet_pos_sent = t_pos
            tweet_neut_sent = t_neut
            tweet_neg_sent = t_neg

            pos_titles = "\n".join(pos_titles)
            neut_titles = "\n".join(neut_titles)
            neg_titles = "\n".join(neg_titles)
            pos_tweets = "\n".join(pos_tweets)
            neut_tweets = "\n".join(neut_tweets)
            neg_tweets = "\n".join(neg_tweets)

            self.neo.create_new_player(db_name, category, player, url, twitter, description,
                                       news_pos_sent, news_neut_sent, news_neg_sent,
                                       tweet_pos_sent, tweet_neut_sent, tweet_neg_sent,
                                       pos_titles, neut_titles, neg_titles,
                                       pos_tweets, neut_tweets, neg_tweets)

    def add_edge_category(self, collection_name, db_name):

        localhost = "mongodb://127.0.0.1:27017"
        mongo_db_name = "players"
        mng = mongodb(localhost, mongo_db_name)
        df = mng.returnColAsDf(collection_name)
        for counter in range(df.shape[0]):
            player1 = df.iloc[counter]['root']
            players2 = df.iloc[counter]['child'].split("-")
            category1 = player1.split("-")
            for p2 in players2:
                #category2 = p2.split("-")
                lst_cat = category1
                self.neo.create_new_edge_cat(db_name, category1, player1, lst_cat, p2)

    def add_edge_entity(self, collection_name, db_name):
        localhost = "mongodb://127.0.0.1:27017"
        mongo_db_name = "players"
        mng = mongodb(localhost, mongo_db_name)
        df = mng.returnColAsDf(collection_name)
        for counter in range(df.shape[0]):
            players_1 = df.iloc[counter]['category'].split("-")
            root = df.iloc[counter]['root']
            player_2 = df.iloc[counter]['player']
            category2 = players_1
            for p in players_1:
                cat1_list = []
                #cat1_list.append(p)
                cat1_list.append(root)
                self.neo.create_new_edge_cat(db_name, cat1_list, p, category2, player_2)

    def add_edge_relations(self, collection_name_1, collection_name_2, collection_name_3, collection_name_4, db_name):
        localhost = "mongodb://127.0.0.1:27017"
        mongo_db_name = "players"
        mng = mongodb(localhost, mongo_db_name)
        txtprc = textProcessing()
        df_2 = mng.returnColAsDf(collection_name_2)
        df_exc = mng.returnColAsDf("excludeWords")
        exc_list = df_exc['word'].to_list()
        epsilon = 0.2
        title_pos = 1.5
        snip_pos = 1
        url_pos = 0.5
        null = None
        s_lst = "2022/01/01".split('/')
        start_date = datetime.date(int(s_lst[0]), int(s_lst[1]), int(s_lst[2]))
        f_lst = "2023/01/01".split('/')
        finish_date = datetime.date(int(f_lst[0]), int(f_lst[1]), int(f_lst[2]))
        date_list = pd.date_range(start_date, finish_date).tolist()
        for counter in range(len(df_2)):
            final_score = 0
            player1 = df_2.iloc[counter]['player']
            # if player1 == "filecoin":
            result = mng.findData(collection_name_1, player1)
            for re in result:
                category1 = re['category'].split("-")
            # print(category1)
            player2 = df_2.iloc[counter]['entity']
            # if player2 == "velero":
            # print(player1)
            # print(player2)
            result = mng.findData(collection_name_1, player2)
            for re in result:
                category2 = re['category'].split("-")
            # print(category2)
            lst = list(eval((df_2.iloc[counter]['linkStatus'])))
            title_final_score = 0
            try:
                for j in range(len(lst) - 1):
                    tmp_title_score = 0
                    title = lst[j]['title']
                    tokens = txtprc.normalizing(title)
                    #print(tokens)
                    for w in exc_list:
                        if w in tokens:
                            tmp_title_score -= epsilon
                            # print(w)
                    #print("after removing exclude words -->", tmp_title_score)
                    if tmp_title_score > -epsilon:
                        p2_lst = player2.lower().split(" ")
                        #print(p2_lst)
                        if len(p2_lst) > 1:
                            if player1 in tokens and p2_lst[0] in tokens and p2_lst[1] in tokens:
                                tmp_title_score += title_pos
                        else:
                            if player1 in tokens and p2_lst[0] in tokens:
                                tmp_title_score += title_pos
                    #print("final ->", tmp_title_score)
                    title_final_score += tmp_title_score
            except Exception as e:
                print(str(e))

            #print(title_final_score)
            snippet_final_score = 0
            try:
                for j in range(len(lst) - 1):
                    tmp_snippet_score = 0
                    snippet = lst[j]['snippet']
                    tokens = txtprc.normalizing(str(snippet))
                    #print(tokens)
                    for w in exc_list:
                        if w in tokens:
                            tmp_snippet_score -= epsilon
                            #print(w)
                    #print("after removing exclude words -->", tmp_snippet_score)
                    if tmp_snippet_score > -epsilon:
                        p2_lst = player2.lower().split(" ")
                        if len(p2_lst) > 1:
                            if player1 in tokens and p2_lst[0] in tokens and p2_lst[1] in tokens:
                                tmp_snippet_score += snip_pos
                        else:
                            if player1 in tokens and p2_lst[0] in tokens:
                                tmp_snippet_score += snip_pos

                    #print("final ->", tmp_snippet_score)
                    snippet_final_score += tmp_snippet_score
            except Exception as e:
                print(str(e))
            url_final_score = 0
            try:
                urls = lst[-1]['urls']
                for url in urls:
                    if str(url).find(player1) != -1:
                        url_final_score += url_pos
                    elif str(url).find("twitter") != -1 or str(url).find("github") != -1 or str(url).find(
                            "linkedin") != -1 or str(url).find("youtube") != -1:
                        url_final_score += url_pos - epsilon
            except:
                pass
            #print(url_final_score)
            final_score = round(((snippet_final_score + title_final_score + url_final_score) / 3), 2)
            print(player1, final_score, player2)

            df_3 = mng.findNewsByEdge(collection_name_3, date_list[0], date_list[-1], player1, player2)
            df_4 = mng.findTweetByEdge(collection_name_4, date_list[0], date_list[-1], player1, player2)
            n_pos, n_neut, n_neg = 0, 0, 0
            t_pos, t_neut, t_neg = 0, 0, 0

            pos_titles = []
            neg_titles = []
            neut_titles = []

            for i in range(df_3.shape[0]):
                news_sent = df_3.iloc[i]['aggLabel']
                if news_sent == "positive":
                    n_pos += 1
                    tmp = "**" + str(df_3.iloc[i]['title']).replace("\"", " ") + "**"
                    pos_titles.append(tmp)
                elif news_sent == "neutral":
                    n_neut += 1
                    tmp = "**" + str(df_3.iloc[i]['title']).replace("\"", " ") + "**"
                    neut_titles.append(tmp)
                elif news_sent == "negative":
                    n_neg += 1
                    tmp = "**" + str(df_3.iloc[i]['title']).replace("\"", " ") + "**"
                    neg_titles.append(tmp)

            pos_tweets = []
            neg_tweets = []
            neut_tweets = []

            for i in range(df_4.shape[0]):
                tweet_sent = df_4.iloc[i]['aggLabel']
                if tweet_sent == "positive":
                    t_pos += 1
                    lst = list(eval((df_4.iloc[i]['tokenizedTweet'])))
                    tmp = "**" + " ".join(lst).replace("\"", " ") + "**"
                    pos_tweets.append(tmp)
                elif tweet_sent == "neutral":
                    t_neut += 1
                    lst = list(eval((df_4.iloc[i]['tokenizedTweet'])))
                    tmp = "**" + " ".join(lst).replace("\"", " ") + "**"
                    neut_tweets.append(tmp)
                elif tweet_sent == "negative":
                    t_neg += 1
                    lst = list(eval((df_4.iloc[i]['tokenizedTweet'])))
                    tmp = "**" + " ".join(lst).replace("\"", " ") + "**"
                    neg_tweets.append(tmp)

            news_pos_sent = n_pos
            news_neut_sent = n_neut
            news_neg_sent = n_neg
            tweet_pos_sent = t_pos
            tweet_neut_sent = t_neut
            tweet_neg_sent = t_neg

            pos_titles = "\n".join(pos_titles)
            neut_titles = "\n".join(neut_titles)
            neg_titles = "\n".join(neg_titles)
            pos_tweets = "\n".join(pos_tweets)
            neut_tweets = "\n".join(neut_tweets)
            neg_tweets = "\n".join(neg_tweets)

            self.neo.create_new_edge_rel(db_name, category1, player1, category2, player2, final_score,
                                         news_pos_sent, news_neut_sent, news_neg_sent,
                                         tweet_pos_sent, tweet_neut_sent, tweet_neg_sent,
                                         pos_titles, neut_titles, neg_titles,
                                         pos_tweets, neut_tweets, neg_tweets)