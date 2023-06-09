import time
import datetime
import yfinance as yf
from ta import add_all_ta_features
from preprocessing import textProcessing
from collections import defaultdict
import math
import networkx as nx
import random
from tqdm import tqdm
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
# import matplotlib.pyplot as plt
from keras import layers
from db import mongodb
import csv
import sys

localhost = "mongodb://127.0.0.1:27017"
db_name = "players"
collection_name_1 = "entities"
collection_name_2 = "relations"
collection_name_3 = "newsByEdge"
collection_name_4 = "newsByNode"
collection_name_5 = "tweetByEdge"
collection_name_6 = "tweetByNode"

txtprc = textProcessing()
mng = mongodb(localhost, db_name)


def computeScore(e1, e2, linkStatus):
    df_exc = mng.returnColAsDf("excludeWords")
    exc_list = df_exc['word'].to_list()
    epsilon = 0.2
    title_pos = 1.5
    snip_pos = 1
    url_pos = 0.5
    null = None
    lst = (list(eval(linkStatus)))
    title_final_score = 0
    try:
        for j in range(len(lst) - 1):
            tmp_title_score = 0
            title = lst[j]['title']
            tokens = txtprc.normalizing(title)
            for w in exc_list:
                if w in tokens:
                    tmp_title_score -= epsilon
            if tmp_title_score > -epsilon:
                p2_lst = e2.lower().split(" ")
                if len(p2_lst) > 1:
                    if e1 in tokens and p2_lst[0] in tokens and p2_lst[1] in tokens:
                        tmp_title_score += title_pos
                else:
                    if e1 in tokens and p2_lst[0] in tokens:
                        tmp_title_score += title_pos
            title_final_score += tmp_title_score
    except Exception as e:
        print(str(e))
    snippet_final_score = 0
    try:
        for j in range(len(lst) - 1):
            tmp_snippet_score = 0
            snippet = lst[j]['snippet']
            tokens = txtprc.normalizing(str(snippet))
            for w in exc_list:
                if w in tokens:
                    tmp_snippet_score -= epsilon
            if tmp_snippet_score > -epsilon:
                p2_lst = e2.lower().split(" ")
                if len(p2_lst) > 1:
                    if e1 in tokens and p2_lst[0] in tokens and p2_lst[1] in tokens:
                        tmp_snippet_score += snip_pos
                else:
                    if e1 in tokens and p2_lst[0] in tokens:
                        tmp_snippet_score += snip_pos
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
    except Exception as e:
        print(str(e))
        pass
    final_score = round(((snippet_final_score + title_final_score + url_final_score) / 3), 2)
    return final_score


def constGraph(df_1, start, end):
    graph = nx.Graph()
    for counter in range(len(df_1)):
        p1 = df_1.iloc[counter]['player']
        p2 = df_1.iloc[counter]['entity']
        tmp_ent = (p2, p1)
        if tmp_ent in en_lst:
            continue
        en_lst.append((p1, p2))
        linkStatus = df_1.iloc[counter]['linkStatus']
        score = computeScore(p1, p2, linkStatus)
        if score > 0:
            news_data = mng.findNewsByEdge(collection_name_3, start, end, p1, p2)
            tweet_data = mng.findTweetByEdge(collection_name_5, start, end, p1, p2)
            weight = score
            news_score = 0
            tweet_score = 0
            # Find weight by computing sentiment of news articles.
            if news_data.shape[0] != 0:
                N = news_data.shape[0]
                pos_score = 0
                neg_score = 0
                for c in range(news_data.shape[0]):
                    try:
                        aggScore = str(news_data.iloc[c]['bodyScore']).replace("[", "").replace("]", "")
                        aggScore = aggScore.split(" ")
                        ext_space = ''
                        while True:
                            if ext_space in aggScore:
                                aggScore.remove(ext_space)
                            else:
                                break
                        pos = float(aggScore[1])
                        neg = float(aggScore[2])
                        neu = float(aggScore[0])
                        arr = np.array([pos, neg, neu])
                        res = np.argmax(arr)
                        if res == 1:
                            pos_score += pos
                        elif res == 2:
                            neg_score += neg
                    except Exception as e:
                        print(str(e))
                        pass
                news_score = (pos_score - neg_score) / N

            if tweet_data.shape[0] != 0:
                N = tweet_data.shape[0]
                pos_score = 0
                neg_score = 0
                for c in range(tweet_data.shape[0]):
                    try:
                        aggScore = str(tweet_data.iloc[c]['aggScore']).replace("[", "").replace("]", "")
                        aggScore = aggScore.split(" ")
                        ext_space = ''
                        while True:
                            if ext_space in aggScore:
                                aggScore.remove(ext_space)
                            else:
                                break
                        pos = float(aggScore[1])
                        neg = float(aggScore[2])
                        neu = float(aggScore[0])
                        arr = np.array([pos, neg, neu])
                        res = np.argmax(arr)
                        if res == 1:
                            pos_score += pos
                        elif res == 2:
                            neg_score += neg
                    except Exception as e:
                        print(str(e))
                        pass
                tweet_score = (pos_score - neg_score) / N
            #weight = weight * math.exp(news_score + tweet_score)
            weight = math.exp(weight * (news_score + tweet_score))
            weight = round(weight, 4)
            # print(weight)
            graph.add_edge(p1, p2, weight=weight)

    nodeToVec(graph, start, end)

def nodeToVec(graph, start, end):
    vocabulary = list(graph.nodes)[::-1]
    vocabulary_lookup = {token: idx for idx, token in enumerate(vocabulary)}
    p = 1 / 3
    q = 1
    num_walks = 1
    num_steps = 3
    walks = random_walk(graph, num_walks, num_steps, p, q, vocabulary_lookup)
    # print(walks)
    # print("Number of walks generated:", len(walks))
    num_negative_samples = 4
    targets, contexts, labels, weights = generate_examples(
        sequences=walks,
        window_size=num_steps,
        num_negative_samples=num_negative_samples,
        vocabulary_size=len(vocabulary),
    )

    batch_size = 64
    dataset = create_dataset(
        targets=targets,
        contexts=contexts,
        labels=labels,
        weights=weights,
        batch_size=batch_size,
    )
    learning_rate = 0.001
    embedding_dim = 32
    num_epochs = 64

    model = create_model(len(vocabulary), embedding_dim)
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate),
        loss=keras.losses.BinaryCrossentropy(from_logits=True),
    )

    keras.utils.plot_model(
        model,
        show_shapes=True,
        show_dtype=True,
        show_layer_names=True,
    )
    history = model.fit(dataset, epochs=num_epochs)
    # plt.plot(history.history["loss"])
    # plt.ylabel("loss")
    # plt.xlabel("epoch")
    # plt.show()
    entity_embeddings = model.get_layer("item_embeddings").get_weights()[0]
    coins_info = findSimilarEnt(entity_embeddings, vocabulary_lookup, vocabulary)
    extractFeature(coins_info, entity_embeddings, vocabulary_lookup, vocabulary, start, end)

def findSimilarEnt(entity_embeddings, vocabulary_lookup, vocabulary):

    dec_coins = ['filecoin', 'storj', 'siacoin', 'arweave']
    dec_coins_embeddings = []
    for item in dec_coins:
        idx = vocabulary_lookup[item]
        dec_coins_embeddings.append(entity_embeddings[idx])

    dec_coins_embeddings = np.array(dec_coins_embeddings)
    similarities = tf.linalg.matmul(
        tf.math.l2_normalize(dec_coins_embeddings),
        tf.math.l2_normalize(entity_embeddings),
        transpose_b=True,
    )
    _, indices = tf.math.top_k(similarities, k=16)
    indices = indices.numpy().tolist()
    coin_similar = defaultdict(list)
    for idx, name in enumerate(dec_coins):
        tmp = []
        # print(name)
        # print("".rjust(len(name), "-"))
        similar_entities = indices[idx]
        for c, entity in enumerate(similar_entities):
            similar_entity = vocabulary[entity]
            tmp.append(similar_entity)
            # print(c, "-->", similar_entity)
        coin_similar[name] = tmp
    return coin_similar

def writeFeatures(fname, row):

    with open("{}.csv".format(fname), "a", newline='') as fp:
        wr = csv.writer(fp)
        wr.writerow(row)

def next_step(graph, previous, current, p, q):

    neighbors = list(graph.neighbors(current))
    weights = []
    for neighbor in neighbors:
        if neighbor == previous:
            weights.append(graph[current][neighbor]["weight"] / p)
        elif graph.has_edge(neighbor, previous):
            weights.append(graph[current][neighbor]["weight"])
        else:
            weights.append(graph[current][neighbor]["weight"] / q)

    w = np.array(weights)
    try:
        probabilities = (np.exp(w)) / (np.exp(w).sum())
        next = np.random.choice(neighbors, size=1, p=probabilities)[0]
    except Exception as e:
        print(str(e))
        N = probabilities.size
        probabilities = np.random.dirichlet(np.ones(N), size=1)[0]
        next = np.random.choice(neighbors, size=1, p=probabilities)[0]
    return next

def random_walk(graph, num_walks, num_steps, p, q, vocabulary_lookup):

    walks = []
    nodes = list(graph.nodes())
    for walk_iteration in range(num_walks):
        random.shuffle(nodes)
        for node in tqdm(
                nodes,
                position=0,
                leave=True,
                desc=f"Random walks iteration {walk_iteration + 1} of {num_walks}",
        ):
            walk = [node]
            while len(walk) < num_steps:
                current = walk[-1]
                previous = walk[-2] if len(walk) > 1 else None
                next = next_step(graph, previous, current, p, q)
                walk.append(next)
            walk = [vocabulary_lookup[token] for token in walk]
            walks.append(walk)
    return walks

def generate_examples(sequences, window_size, num_negative_samples, vocabulary_size):

    example_weights = defaultdict(int)
    # Iterate over all sequences (walks).
    for sequence in tqdm(
            sequences,
            position=0,
            leave=True,
            desc=f"Generating postive and negative examples",
    ):
        # Generate positive and negative skip-gram pairs for a sequence (walk).
        pairs, labels = keras.preprocessing.sequence.skipgrams(
            sequence,
            vocabulary_size=vocabulary_size,
            window_size=window_size,
            negative_samples=num_negative_samples,
        )
        for idx in range(len(pairs)):
            pair = pairs[idx]
            label = labels[idx]
            target, context = min(pair[0], pair[1]), max(pair[0], pair[1])
            if target == context:
                continue
            entry = (target, context, label)
            example_weights[entry] += 1

    targets, contexts, labels, weights = [], [], [], []
    for entry in example_weights:
        weight = example_weights[entry]
        target, context, label = entry
        targets.append(target)
        contexts.append(context)
        labels.append(label)
        weights.append(weight)

    return np.array(targets), np.array(contexts), np.array(labels), np.array(weights)


def create_dataset(targets, contexts, labels, weights, batch_size):
    inputs = {
        "target": targets,
        "context": contexts,
    }
    dataset = tf.data.Dataset.from_tensor_slices((inputs, labels, weights))
    dataset = dataset.shuffle(buffer_size=batch_size * 2)
    dataset = dataset.batch(batch_size, drop_remainder=True)
    dataset = dataset.prefetch(tf.data.AUTOTUNE)
    return dataset


def create_model(vocabulary_size, embedding_dim):
    inputs = {
        "target": layers.Input(name="target", shape=(), dtype="int32"),
        "context": layers.Input(name="context", shape=(), dtype="int32"),
    }
    embed_item = layers.Embedding(
        input_dim=vocabulary_size,
        output_dim=embedding_dim,
        embeddings_initializer="he_normal",
        embeddings_regularizer=keras.regularizers.l2(1e-6),
        name="item_embeddings",
    )
    target_embeddings = embed_item(inputs["target"])
    context_embeddings = embed_item(inputs["context"])
    logits = layers.Dot(axes=1, normalize=False, name="dot_similarity")(
        [target_embeddings, context_embeddings]
    )
    model = keras.Model(inputs=inputs, outputs=logits)
    return model

def extractFeature(coins_info, entity_embeddings, vocabulary_lookup, vocabulary, start, end):

    dec_coins = ['filecoin', 'storj', 'siacoin', 'arweave']
    for coin in dec_coins:

        tmp_lst = coins_info[coin]
        all_emb = np.zeros((16, 32))
        for cnt, item in enumerate(tmp_lst):
            idx = vocabulary_lookup[item]
            vec = entity_embeddings[idx]
            all_emb[cnt, :] = vec
        for row in all_emb:
            writeFeatures("allData/features-14-1/{}_1".format(coin), row)

        date_list = pd.date_range(start, end).tolist()
        delta = datetime.timedelta(days=1)

        for date in date_list[:-1]:

            all_scores = []
            for entity in tmp_lst:
                news_pos_score = 0
                news_neg_score = 0
                tweet_pos_score = 0
                tweet_neg_score = 0
                start_tmp = date
                end_tmp = date + delta
                news_data = mng.findNewsByNode(collection_name_4, start_tmp, end_tmp, entity)
                tweet_data = mng.findTweetByNode(collection_name_6, start_tmp, end_tmp, entity)
                news_score = 0
                if news_data.shape[0] != 0:
                    N = news_data.shape[0]
                    for c1 in range(news_data.shape[0]):
                        try:
                            aggScore = str(news_data.iloc[c1]['bodyScore']).replace("[", "").replace("]", "")
                            aggScore = aggScore.split(" ")
                            ext_space = ''
                            while True:
                                if ext_space in aggScore:
                                    aggScore.remove(ext_space)
                                else:
                                    break
                            pos = float(aggScore[1])
                            neg = float(aggScore[2])
                            neu = float(aggScore[0])
                            arr = np.array([pos, neg, neu])
                            res = np.argmax(arr)
                            if res == 1:
                                news_pos_score += pos
                            elif res == 2:
                                news_neg_score += neg
                        except Exception as e:
                            print(str(e))
                            pass
                    news_score = (news_pos_score - news_neg_score) / N

                all_scores.append(news_score)

                tweet_score = 0
                if tweet_data.shape[0] != 0:
                    N = tweet_data.shape[0]
                    for c2 in range(tweet_data.shape[0]):
                        try:
                            aggScore = str(tweet_data.iloc[c2]['aggScore']).replace("[", "").replace("]", "")
                            aggScore = aggScore.split(" ")
                            ext_space = ''
                            while True:
                                if ext_space in aggScore:
                                    aggScore.remove(ext_space)
                                else:
                                    break
                            pos = float(aggScore[1])
                            neg = float(aggScore[2])
                            neu = float(aggScore[0])
                            arr = np.array([pos, neg, neu])
                            res = np.argmax(arr)
                            if res == 1:
                                tweet_pos_score += pos
                            elif res == 2:
                                tweet_neg_score += neg
                        except Exception as e:
                            print(str(e))
                            pass
                    tweet_score = (tweet_pos_score - tweet_neg_score) / N
                all_scores.append(tweet_score)
            row = np.array(all_scores)
            writeFeatures("allData/features-14-1/{}_2".format(coin), row)

        fin_data_1 = mng.findFinanceByDate("{}Finance".format(coin), start, end)
        fin_data_1 = fin_data_1.drop(['_id', 'Date'], axis=1)
        for cnt in range(fin_data_1.shape[0]):
            row_1 = fin_data_1.iloc[cnt]
            writeFeatures("allData/features-14-1/{}_3".format(coin), row_1)

        p1 = mng.findFinanceExactByDate("{}Finance".format(coin), end - delta)
        p2 = mng.findFinanceExactByDate("{}Finance".format(coin), end + (10*delta))
        label = 0
        f_price = float(p1.iloc[0]['Adj Close'])
        s_price = float(p2.iloc[0]['Adj Close'])
        if s_price > f_price:
            label = 1
        writeFeatures("allData/labels-14-10/{}".format(coin), [label])

if __name__ == "__main__":

    df_1 = mng.returnColAsDf(collection_name_2)
    s_lst = "2022/01/01".split('/')
    start_date = datetime.date(int(s_lst[0]), int(s_lst[1]), int(s_lst[2]))
    f_lst = "2023/01/01".split('/')
    finish_date = datetime.date(int(f_lst[0]), int(f_lst[1]), int(f_lst[2]))
    date_list = pd.date_range(start_date, finish_date).tolist()
    print(date_list)
    beta = datetime.timedelta(days=7)
    for i, date in enumerate(date_list[:-8]):
        start = date
        print("".rjust(len(str(start)), "*"))
        print(start)
        end = date + beta
        print(end)
        print("".rjust(len(str(end)), "*"))
        en_lst = []
        constGraph(df_1, start, end)

