import torch
import json
from transformers import T5Tokenizer, T5ForConditionalGeneration, T5Config
from transformers import BertTokenizer, BertForSequenceClassification
import numpy as np
import torch.nn as tornn
from db import mongodb
import threading
import pandas as pd

localhost = "mongodb://127.0.0.1:27017"
db_name = "players"
collection_name = "newsByNode"
mng = mongodb(localhost, db_name)


def sumSent(start, end):

    df = mng.returnColAsDf(collection_name)
    for counter in range(start, end):
        try:
            chk = str(df.iloc[counter]['summary'])
            if chk == "nan":
                print(counter)
                model = T5ForConditionalGeneration.from_pretrained('t5-small')
                tokenizer = T5Tokenizer.from_pretrained('t5-small')
                device = torch.device('cpu')
                _id = df['_id'][counter]
                title = str(df.iloc[counter]['title'])
                text = str(df.iloc[counter]['text'])
                preprocess_text = text.strip().replace("\n", "")
                maxLength = int(len(preprocess_text.split(" ")) / 2)
                minLength = int(len(preprocess_text.split(" ")) / 8)
                t5_prepared_Text = "summarize: " + preprocess_text
                # print(preprocess_text)
                tokenized_text = tokenizer.encode(t5_prepared_Text, return_tensors="pt", max_length=2048,
                                                  truncation=True).to(device)
                summary_ids = model.generate(tokenized_text,
                                             num_beams=6,
                                             min_length=minLength,
                                             max_length=maxLength,
                                             length_penalty=5.
                                             )
                summary = tokenizer.decode(summary_ids[0])
                mng.addSummary(collection_name, _id, summary)
                print("\n main_summary: ", summary, end="\n")
                summary_tmp = str(summary).split(" ")
                summary_lst = summary_tmp[:512]
                summary = " ".join(summary_lst)
                # print("\n truncated_summary: ", summary, end="\n")
                try:
                    finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone', num_labels=3)
                    tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')
                    input1 = tokenizer(title, return_tensors="pt", padding=True)
                    input2 = tokenizer(summary, return_tensors="pt", padding=True)
                    sent_scores_title = finbert(**input1)[0]
                    sent_scores_text = finbert(**input2)[0]
                    labels = {0: 'neutral', 1: 'positive', 2: 'negative'}
                    nmpy_title = sent_scores_title.detach().numpy()
                    nmpy_text = sent_scores_text.detach().numpy()
                    x1 = nmpy_title[0]
                    x2 = nmpy_text[0]
                    sft_title = (np.exp(x1) / np.exp(x1).sum())
                    sft_text = (np.exp(x2) / np.exp(x2).sum())
                    mng.addTitleSentimentScore(collection_name, _id, str(sft_title))
                    mng.addBodySentimentScore(collection_name, _id, str(sft_text))
                    med_snt = np.vstack((sft_title, sft_text))
                    final_snt = np.mean(med_snt, axis=0)
                    mng.addAggSentimentScore(collection_name, _id, str(final_snt))
                    mng.addTitleSentimentLabel(collection_name, _id, str(labels[np.argmax(sft_title)]))
                    mng.addBodySentimentLabel(collection_name, _id, str(labels[np.argmax(sft_text)]))
                    mng.addAggSentimentLabel(collection_name, _id, str(labels[np.argmax(final_snt)]))
                except Exception as e:
                    print(str(e))
                    pass

        except Exception as e:
            print(str(e))
            pass
if __name__ == "__main__":


    batch_size = 250
    total = 1000
    counter = int(total/batch_size)
    threads = []
    for i in range(counter):
        threads.append(threading.Thread(target=sumSent, args=(i*batch_size, (i+1)*batch_size)))
        threads[i].start()
    for j in range(counter):
        threads[j].join()