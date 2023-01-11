import torch
import json
from transformers import T5Tokenizer, T5ForConditionalGeneration,T5Config
from transformers import BertTokenizer, BertForSequenceClassification
import numpy as np
import torch.nn as tornn


model = T5ForConditionalGeneration.from_pretrained('t5-large')
tokenizer = T5Tokenizer.from_pretrained('t5-large')

text = """According to Digital Coin Price, the estimation is that the STORJ price will rise to $2.27 by 2025. 
Furthermore, the estimation is that the coin will soar to over $6 by 2031; obviously"""

device =torch.device('cpu')
preprocess_text = text.strip().replace("\n", "")
t5_prepared_Text = "summarize: "+preprocess_text
tokenized_text = tokenizer.encode(t5_prepared_Text, return_tensors="pt", max_length=2048, truncation=True).to(device)
summary_ids = model.generate(tokenized_text,
                            num_beams=6,
                            min_length=50,
                            max_length=100,
                            length_penalty=2.0,
                            )
print(summary_ids, end="\n")
summary = tokenizer.decode(summary_ids[0])
print(summary)
finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-tone',num_labels=3)
tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-tone')
inputs = tokenizer(summary, return_tensors="pt", padding=True)
sent_scores = finbert(**inputs)[0]
print(sent_scores)
sftmx = tornn.Softmax(dim=0)
b = sftmx(sent_scores)
print(b)
labels = {0: 'neutral', 1: 'positive', 2: 'negative'}
print(labels[np.argmax(sent_scores.detach().numpy())])
