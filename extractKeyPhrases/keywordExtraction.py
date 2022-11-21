from keybert import KeyBERT
from db import mongodb
import pandas as pd
import argparse
from sentence_transformers import SentenceTransformer
import threading

sent_trans = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
keyBERT_model = KeyBERT(model=sent_trans)

def keyPhraseExtractor(db_url, db_name, collection_name, start, end, min_length, max_length, num_keyphrase):

    mng = mongodb(db_url, db_name)
    # getting the related collection as a pandas dataframe
    df = mng.returnColAsDf(collection_name)
    df['content'] = df['title'] + df['text']
    for counter in range(start, end):
        _id = df.iloc[counter]['_id']
        news = df.iloc[counter]['content']
        # removing extra spaces
        finalDoc = ' '.join(news.split())
        extractedKeyPhrases = keyBERT_model.extract_keywords(finalDoc, stop_words='english',
                                    keyphrase_ngram_range=(min_length, max_length),
                                    use_mmr=True,
                                    diversity=0.7,
                                    top_n=num_keyphrase
                                                             )
        sortedeKeyPhrases = sorted(extractedKeyPhrases, key=lambda tup: (-tup[1], tup[0]))
        result = [{"phrase": kp[0], "score": kp[1]} for kp in sortedeKeyPhrases]
        print(result)
        mng.addKeyPhrasesbyId(collection_name, _id, result)

if __name__=="__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input File Name")
    args = parser.parse_args()
    metadata = pd.read_csv(args.input)
    db_url = metadata.iloc[0]['db_url']
    db_name = metadata.iloc[0]['db_name']
    collection_name = metadata.iloc[0]['collection_name']
    num_threads = metadata.iloc[0]['num_threads']
    num_tasks = metadata.iloc[0]['sub_task']
    min_length = metadata.iloc[0]['min_length']
    max_length = metadata.iloc[0]['max_length']
    num_keyphrase = metadata.iloc[0]['num_keyphrase']
    #initializing threads
    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=keyPhraseExtractor, args=(db_url, db_name, collection_name, i*num_tasks, (i+1)*num_tasks, min_length, max_length, num_keyphrase))
        threads.append(t)
        threads[i].start()
