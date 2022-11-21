from db import mongodb
localhost = "mongodb://127.0.0.1:27017"
db_name = "socialMedia"
mng = mongodb(localhost, db_name)
collectionName = "cryptocurrency"

def retrieveHighScore():

    lst = []
    dic = {}
    df = mng.returnSelectedColAsDf(collectionName)
    data1 = df['editedTweet']
    data = df['twoToFourKeyPhrase']
    for co in range(df.shape[0]):
        print(data1.iloc[co])
        print(data.iloc[co])
    # for counter in range(df.shape[0]):
    #     if type(data.iloc[counter]) == str:
    #         tmp = list(eval(data.iloc[counter]))
    #         li = [d['phrase'] for d in tmp if d['score'] > 0.7]
    #         for itm in li:
    #             lst.append(itm)
    #     elif type(data.iloc[counter]) == list:
    #         tmp = data.iloc[counter]
    #         li = [d['phrase'] for d in tmp if d['score'] > 0.7]
    #         for itm in li:
    #             lst.append(itm)
    # dic['highScorePhrases'] = lst
    # print(len(lst))
    # mng.writeOne("targetCoinsKeybert", dic)

if __name__=="__main__":

    retrieveHighScore()
