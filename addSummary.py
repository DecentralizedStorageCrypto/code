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

def addSummaryToNews():
    df = mng.returnColAsDf(collection_name)
    for counter in range(df.shape[0]):
        _id = df.iloc[counter]['_id']
        try:
            text = str(df.iloc[counter]['text'])
            print(text)
            preprocess_text = text.strip().replace("\n", "")
            maxLength = int(len(preprocess_text.split(" ")) / 2)
            minLength = int(len(preprocess_text.split(" ")) / 6)
            print(preprocess_text)
            t5_prepared_Text = "summarize: " + preprocess_text
            tokenized_text = tokenizer.encode(t5_prepared_Text, return_tensors="pt", max_length=2048,
                                              truncation=True).to(
                device)
            summary_ids = model.generate(tokenized_text,
                                         num_beams=6,
                                         min_length=minLength,
                                         max_length=maxLength,
                                         length_penalty=0.75
                                         )
            # print(summary_ids, end="\n")
            summary = tokenizer.decode(summary_ids[0])
            print("\n\n summary: ", summary, end="\n")
        except:
            summary = " "
        mng.addSummary(collection_name, _id, str(summary))

if __name__ == "__main__":
    addSummaryToNews()
