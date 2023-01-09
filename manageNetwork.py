from neoHandler import NEO4J
from db import mongodb
from preprocessing import textProcessing

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
        print(df_1)
        for counter in range(df_1.shape[0]):
            player1 = df_1.iloc[counter]['root']
            players2 = df_1.iloc[counter]['child'].split("-")
            category1 = player1.split("-")
            self.neo.create_new_player(db_name, category1, player1)
            for p2 in players2:
                category2 = p2.split("-")
                lst_cat = category1 + category2
                self.neo.create_new_player(db_name, lst_cat, p2)

    def add_node_entity(self, collection_name, db_name):
        localhost = "mongodb://127.0.0.1:27017"
        mongo_db_name = "players"
        mng = mongodb(localhost, mongo_db_name)
        df = mng.returnColAsDf(collection_name)
        print(df)
        for counter in range(df.shape[0]):
            player = df.iloc[counter]['player']
            category = df.iloc[counter]['category'].split("-")
            url = str(df.iloc[counter]['link'])
            twitter = str(df.iloc[counter]['twitter'])
            description = str(df.iloc[counter]['description'])
            self.neo.create_new_player(db_name, category, player, url, twitter, description)

    def add_edge_category(self, collection_name, db_name):
        localhost = "mongodb://127.0.0.1:27017"
        mongo_db_name = "players"
        mng = mongodb(localhost, mongo_db_name)
        df = mng.returnColAsDf(collection_name)
        print(df)
        for counter in range(df.shape[0]):
            player1 = df.iloc[counter]['root']
            players2 = df.iloc[counter]['child'].split("-")
            category1 = player1.split("-")
            for p2 in players2:
                category2 = p2.split("-")
                lst_cat = category1 + category2
                self.neo.create_new_edge_cat(db_name, category1, player1, lst_cat, p2)

    def add_edge_entity(self, collection_name, db_name):
        localhost = "mongodb://127.0.0.1:27017"
        mongo_db_name = "players"
        mng = mongodb(localhost, mongo_db_name)
        df = mng.returnColAsDf(collection_name)
        print(df)
        for counter in range(df.shape[0]):
            players_1 = df.iloc[counter]['category'].split("-")
            root = df.iloc[counter]['root']
            player_2 = df.iloc[counter]['player']
            category2 = players_1
            for p in players_1:
                cat1_list = []
                cat1_list.append(p)
                cat1_list.append(root)
                self.neo.create_new_edge_cat(db_name, cat1_list, p, category2, player_2)

    def add_edge_relations(self, collection_name_1, collection_name_2, db_name):
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
            lst = (list(eval((df_2.iloc[counter]['linkStatus']))))
            title_final_score = 0
            try:
                for j in range(len(lst) - 1):
                    tmp_title_score = 0
                    title = lst[j]['title']
                    tokens = txtprc.normalizing(title)
                    print(tokens)
                    for w in exc_list:
                        if w in tokens:
                            tmp_title_score -= epsilon
                            # print(w)
                    print("after removing exclude words -->", tmp_title_score)
                    if tmp_title_score > -epsilon:
                        p2_lst = player2.lower().split(" ")
                        print(p2_lst)
                        if len(p2_lst) > 1:
                            if player1 in tokens and p2_lst[0] in tokens and p2_lst[1] in tokens:
                                tmp_title_score += title_pos
                        else:
                            if player1 in tokens and p2_lst[0] in tokens:
                                tmp_title_score += title_pos
                    print("final ->", tmp_title_score)
                    title_final_score += tmp_title_score
            except:
                pass

            print(title_final_score)
            snippet_final_score = 0
            try:
                for j in range(len(lst) - 1):
                    tmp_snippet_score = 0
                    snippet = lst[j]['snippet']
                    tokens = txtprc.normalizing(str(snippet))
                    print(tokens)
                    for w in exc_list:
                        if w in tokens:
                            tmp_snippet_score -= epsilon
                            print(w)
                    print("after removing exclude words -->", tmp_snippet_score)
                    if tmp_snippet_score > -epsilon:
                        p2_lst = player2.lower().split(" ")
                        if len(p2_lst) > 1:
                            if player1 in tokens and p2_lst[0] in tokens and p2_lst[1] in tokens:
                                tmp_snippet_score += snip_pos
                        else:
                            if player1 in tokens and p2_lst[0] in tokens:
                                tmp_snippet_score += snip_pos

                    print("final ->", tmp_snippet_score)
                    snippet_final_score += tmp_snippet_score
            except:
                pass
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
            print(url_final_score)
            final_score = round(((snippet_final_score + title_final_score + url_final_score) / 3), 2)
            print(player1, final_score, player2)
            self.neo.create_new_edge_rel(db_name, category1, player1, category2, player2, final_score)