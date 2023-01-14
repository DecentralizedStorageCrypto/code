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

for counter in range(46, 47):
    title = str(df.iloc[counter]['title'])
    text = str(df.iloc[counter]['text'])
    key_phrases = df.iloc[counter]['KeyPhrase']
    print(title)
    preprocess_text = text.strip().replace("\n", "")
    maxLength = len(preprocess_text.split(" ")) / 3
    minLength = len(preprocess_text.split(" ")) / 6
    print(preprocess_text)
    t5_prepared_Text = "summarize: " + preprocess_text
    tokenized_text = tokenizer.encode(t5_prepared_Text, return_tensors="pt", max_length=2048, truncation=True).to(
        device)
    summary_ids = model.generate(tokenized_text,
                                 num_beams=8,
                                 min_length=minLength,
                                 max_length=maxLength,
                                 length_penalty=2.0,
                                 )
    #print(summary_ids, end="\n")
    summary = tokenizer.decode(summary_ids[0])
    print("\n\n summary: ", summary)
    finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone', num_labels=3)
    tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')

    input1 = tokenizer(title, return_tensors="pt", padding=True)
    input2 = tokenizer(summary, return_tensors="pt", padding=True)
    sent_scores_title = finbert(**input1)[0]
    sent_scores_text = finbert(**input2)[0]
    # print(sent_scores_title)
    # print(sent_scores_text)
    phrase_score_list = []
    labels = {0: 'neutral', 1: 'positive', 2: 'negative'}
    for item in key_phrases:
        phrase = item['phrase']
        input = tokenizer(phrase, return_tensors="pt", padding=True)
        sent_scores_phrase = finbert(**input)[0]
        nmpy_phrase = sent_scores_phrase.detach().numpy()
        x = nmpy_phrase[0]
        sft_phrase = (np.exp(x) / np.exp(x).sum())
        print(phrase, "-->", sent_scores_phrase, labels[np.argmax(sft_phrase)], end="\n\n\n")
        phrase_score_list.append(sft_phrase)
    #print(phrase_score_list)
    phrase_nmp = np.array(phrase_score_list)
    final_snt_phrase = np.mean(phrase_nmp, axis=0)
    print("The average sentiment score of key phrases is: ", final_snt_phrase, end="\n\n\n")
    nmpy_title = sent_scores_title.detach().numpy()
    nmpy_text = sent_scores_title.detach().numpy()
    x1 = nmpy_title[0]
    x2 = nmpy_text[0]
    sft_title = (np.exp(x1) / np.exp(x1).sum())
    sft_text = (np.exp(x2) / np.exp(x2).sum())
    print("The sentiment score of title is: ", sft_title, end="\n\n\n")
    print("The sentiment score of summary is: ", sft_text, end="\n\n\n")
    med_snt = np.vstack((sft_title, sft_text, final_snt_phrase))
    print(med_snt, end="\n\n\n")
    final_snt = np.mean(med_snt, axis=0)
    print("The average sentiment score of title, key phrases and summary is: ", final_snt, end="\n\n\n")
    print("The average sentiment of key phrases is:", labels[np.argmax(final_snt_phrase)], end="\n\n\n")
    print("The sentiment of title is:", labels[np.argmax(sft_title)], end="\n\n\n")
    print("The sentiment of summary is:", labels[np.argmax(sft_text)], end="\n\n\n")
    print("The average sentiment of title, key phrases, and summary, is:", labels[np.argmax(final_snt)], end="\n\n\n")