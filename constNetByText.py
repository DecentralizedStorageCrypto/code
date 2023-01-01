from neoHandler import NEO4J
import logging
import sys
import pandas as pd
from db import mongodb
from preprocessing import textProcessing

localhost = "mongodb://127.0.0.1:27017"
db_name = "players"
mng = mongodb(localhost, db_name)
collection_name_1 = "entities"
collection_name_2 = "relationsV2"
txtprc = textProcessing()
bolt_url = "bolt://localhost:7687"
user = "neo4j"
password = "228218"
NEO4J.enable_log(logging.INFO, sys.stdout)
neo = NEO4J(bolt_url, user, password)
db_name = "networkbytext"

# neo.clear_graph(db_name)
# sys.exit()

def addToNetwork():

    df_1 = mng.returnColAsDf(collection_name_1)
    for counter in range(df_1.shape[0]):
        player = df_1.iloc[counter]['player']
        print(player)
        category = df_1.iloc[counter]['category'].split("-")
        url = str(df_1.iloc[counter]['link'])
        twitter = str(df_1.iloc[counter]['twitter'])
        des = str(df_1.iloc[counter]['description'])
        neo.create_new_player(db_name, category, player, url, twitter, des)

def constRelations():

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
        #if player1 == "filecoin":
        result = mng.findCategory(collection_name_1, player1)
        for re in result:
            category1 = str(re['category']).split("-")
        # print(category1)
        player2 = df_2.iloc[counter]['entity']
        #if player2 == "velero":
            # print(player1)
            # print(player2)
        result = mng.findCategory(collection_name_1, player2)
        for re in result:
            category2 = str(re['category']).split("-")
        # print(category2)
        lst = (list(eval((df_2.iloc[counter]['linkStatus']))))
        title_final_score = 0
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
        print(title_final_score)
        snippet_final_score = 0
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
        url_final_score = 0
        urls = lst[-1]['urls']
        for url in urls:
            if str(url).find(player1) != -1:
                url_final_score += url_pos
            elif str(url).find("twitter") != -1 or str(url).find("github") != -1 or str(url).find(
                    "linkedin") != -1 or str(url).find("youtube") != -1:
                url_final_score += url_pos - epsilon
        print(url_final_score)
        final_score = round(((snippet_final_score + title_final_score + url_final_score) / 3), 2)
        print(player1, final_score, player2)
        neo.create_new_edge(db_name, category1, player1, category2, player2, final_score)


if __name__ == "__main__":
    addToNetwork()
    constRelations()