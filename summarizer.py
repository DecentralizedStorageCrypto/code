import torch
import json
from transformers import T5Tokenizer, T5ForConditionalGeneration,T5Config
from transformers import BertTokenizer, BertForSequenceClassification
import numpy as np

model = T5ForConditionalGeneration.from_pretrained('t5-large')
tokenizer = T5Tokenizer.from_pretrained('t5-large')

text = """ Like most assets, it is always challenging to make a long-term prediction. 
The same situation is more difficult for risky assets like cryptocurrencies. 
It is even harder for a small coin in an industry that is no longer in a growth mode. 
According to Digital Coin Price, the estimation is that the STORJ price will rise to $2.27 by 2025. 
Furthermore, the estimation is that the coin will soar to over $6 by 2031; obviously, 
these estimates should always be taken with a grain of salt.
"""

device =torch.device('cpu')
preprocess_text = text.strip().replace("\n", "")
t5_prepared_Text = "summarize: "+preprocess_text
tokenized_text = tokenizer.encode(t5_prepared_Text, return_tensors="pt", max_length=2048, truncation=True).to(device)
summary_ids = model.generate(tokenized_text,
                            num_beams=4,
                            min_length=80,
                            max_length=200,
                            length_penalty=2.0,
                            )

print(summary_ids, end="\n")
output = tokenizer.decode(summary_ids[0])
print(output)

