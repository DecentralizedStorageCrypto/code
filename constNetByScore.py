from neoHandler import NEO4J
import logging
import sys
import pandas as pd
from db import mongodb

localhost = "mongodb://127.0.0.1:27017"
db_name = "players"
mng = mongodb(localhost, db_name)
collection_name_1 = "entities"
collection_name_2 = "relationsV1"
bolt_url = "bolt://localhost:7687"
user = "neo4j"
password = "228218"
NEO4J.enable_log(logging.INFO, sys.stdout)
neo = NEO4J(bolt_url, user, password)
db_name = "networkbyscore"

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
    for counter in range(len(df_2)):
        player1 = df_2.iloc[counter]['player']
        # if player1 == "filecoin":
        # print(player1)
        result = mng.findCategory(collection_name_1, player1)
        for re in result:
            category1 = str(re['category']).split("-")
        # print(category1)
        player2 = df_2.iloc[counter]['entity']
        # if player2 == "storj":
        result = mng.findCategory(collection_name_1, player2)
        for re in result:
            category2 = str(re['category']).split("-")
        # print(category2)
        repu = df_2.iloc[counter]['repu']
        with_entitiy_score = df_2.iloc[counter]['linkScore']
        relScore = with_entitiy_score / repu
        final_score = round(relScore, 6)
        if final_score > 0:
            print(player1, final_score, player2)
            neo.create_new_edge(db_name, category1, player1, category2, player2, final_score)

if __name__ == "__main__":
    addToNetwork()
    constRelations()