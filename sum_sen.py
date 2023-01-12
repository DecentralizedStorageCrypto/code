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

for counter in range(23,24):

    title = str(df.iloc[counter]['title'])
    text = str(df.iloc[counter]['text'])
    print(title)

    preprocess_text = text.strip().replace("\n", "")
    maxLength = len(preprocess_text.split(" ")) / 2
    print(preprocess_text)
    t5_prepared_Text = "summarize: " + preprocess_text
    tokenized_text = tokenizer.encode(t5_prepared_Text, return_tensors="pt", max_length=2048, truncation=True).to(
        device)
    summary_ids = model.generate(tokenized_text,
                                 num_beams=8,
                                 min_length=100,
                                 max_length=maxLength
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
    nmpy_text = sent_scores_text.detach().numpy()
    x1 = nmpy_title[0]
    x2 = nmpy_text[0]
    sft_title = (np.exp(x1) / np.exp(x1).sum())
    sft_text = (np.exp(x2) / np.exp(x2).sum())
    med_snt = np.vstack((sft_title, sft_text))
    print(med_snt)
    final_snt = np.mean(med_snt, axis=0)
    print(final_snt)
    labels = {0: 'neutral', 1: 'positive', 2: 'negative'}
    print(labels[np.argmax(sft_title)])
    print(labels[np.argmax(sft_text)])
    print(labels[np.argmax(final_snt)])