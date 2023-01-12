import torch
import json
from transformers import T5Tokenizer, T5ForConditionalGeneration,T5Config
from transformers import BertTokenizer, BertForSequenceClassification
import numpy as np
import torch.nn as tornn
from db import mongodb


model = T5ForConditionalGeneration.from_pretrained('t5-large')
tokenizer = T5Tokenizer.from_pretrained('t5-large')
device = torch.device('cpu')
localhost = "mongodb://127.0.0.1:27017"
db_name = "news"
collection_name = "filecoinNews"

mng = mongodb(localhost, db_name)

df = mng.returnColAsDf(collection_name)

for counter in range(df.shape[0]):

    title = str(df.iloc[counter]['title'])
    text = str(df.iloc[counter]['title'])
    print(title)
    print(text)
    preprocess_text = text.strip().replace("\n", "")
    t5_prepared_Text = "summarize: " + preprocess_text
    tokenized_text = tokenizer.encode(t5_prepared_Text, return_tensors="pt", max_length=2048, truncation=True).to(
        device)
    summary_ids = model.generate(tokenized_text,
                                 num_beams=4,
                                 min_length=50,
                                 max_length=100,
                                 length_penalty=2.0,
                                 )
    #print(summary_ids, end="\n")

    summary = tokenizer.decode(summary_ids[0])
    print(summary)
    finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone', num_labels=3)
    tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')

    input1 = tokenizer(title, return_tensors="pt", padding=True)
    input2 = tokenizer(summary, return_tensors="pt", padding=True)
    sent_scores_title = finbert(**input1)[0]
    sent_scores_text = finbert(**input2)[0]

    print(sent_scores_title)
    print(sent_scores_text)

    nmpy_title = sent_scores_title.detach().numpy()
    nmpy_text = sent_scores_title.detach().numpy()
    x1 = nmpy_title[0]
    x2 = nmpy_text[0]
    sft_title = (np.exp(x1) / np.exp(x1).sum())
    sft_text = (np.exp(x2) / np.exp(x2).sum())
    final_sent = np.concatenate((sft_title, sft_text), axis=0)
    print(final_sent)
    break
    # labels = {0: 'neutral', 1: 'positive', 2: 'negative'}
    # print(labels[np.argmax(sent_scores.detach().numpy())])
