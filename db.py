from pymongo import MongoClient
import pandas as pd
class mongodb:

    def __init__(self, client, db):
        self.client = MongoClient(client)
        self.db = self.client[db]

    def writeOne(self, collection, data):
        collection = self.db[collection]
        collection.insert_one(data)

    def writMany(self, collection, data):
        collection = self.db[collection]
        collection.insert_many(data)

    def returnCorsur(self, collection):
        print(collection)
        collection = self.db[collection]
        data = collection.find({})
        return list(data)

    def returnColAsDf(self, collection):
        #print(collection)
        collection = self.db[collection]
        data = collection.find({})
        df = pd.DataFrame(list(data))
        return df
    def returnSpecialColAsDf(self, collection):
        print(collection)
        collection = self.db[collection]
        data = collection.find({'text':{'$regex':'Filecoin'}})
        df = pd.DataFrame(list(data))
        return df

    def findData(self, collection, player):
        collection = self.db[collection]
        corsur = collection.find({'player': player})
        return corsur

    def addSummary(self, collection ,id, summary):
        collection = self.db[collection]
        collection.update_one({'_id': id},{"$set": {'summary': str(summary)}})

    def addTitleSentimentScore(self, collection ,id, sft_title):
        collection = self.db[collection]
        collection.update_one({'_id': id},{"$set": {'titleScore': sft_title}})

    def addBodySentimentScore(self, collection ,id, sft_text):
        collection = self.db[collection]
        collection.update_one({'_id': id},{"$set": {'bodyScore': sft_text}})

    def addAggSentimentScore(self, collection ,id, final_snt):
        collection = self.db[collection]
        collection.update_one({'_id': id},{"$set": {'aggScore': final_snt}})

    def addTitleSentimentLabel(self, collection ,id, sft_title):
        collection = self.db[collection]
        collection.update_one({'_id': id},{"$set": {'titleLabel': sft_title}})

    def addBodySentimentLabel(self, collection ,id, sft_text):
        collection = self.db[collection]
        collection.update_one({'_id': id},{"$set": {'bodyLabel': sft_text}})

    def addAggSentimentLabel(self, collection ,id, final_snt):
        collection = self.db[collection]
        collection.update_one({'_id': id},{"$set": {'aggLabel': final_snt}})


    def addTokenizedTextbyId(self, collection ,id,tokenizedText):
        collection = self.db[collection]
        collection.update_one({'_id': id},{"$set": {'tokenizedText': str(tokenizedText)}})

    def addKeyPhrasesbyId(self, collection, id, keyPhrases):
        collection = self.db[collection]
        collection.update_one({'_id': id}, {"$set": {'KeyPhrase': keyPhrases }})

    def addTwoToFourKeyPhrasesbyId(self, collection, id, keyPhrases):
            collection = self.db[collection]
            collection.update_one({'_id': id}, {"$set": {'twoToFourKeyPhrase': keyPhrases}})

    def addTwoToSixKeyPhrasesbyId(self, collection, id, keyPhrases):
        collection = self.db[collection]
        collection.update_one({'_id': id}, {"$set": {'twoToSixKeyPhrase': keyPhrases}})

    def addEditedTweet(self, collection, id, editedTweet):
        collection = self.db[collection]
        collection.update_one({'_id': id}, {"$set": {'editedTweet': editedTweet}})

    def addTokenizedTweet(self, collection, id, tokenizedTweet):
        collection = self.db[collection]
        collection.update_one({'_id': id}, {"$set": {'tokenizedTweet': tokenizedTweet}})

    def addAggScore(self, collection, id, score):
        collection = self.db[collection]
        collection.update_one({'_id': id}, {"$set": {'aggrScore': score}})

    def addScoreOne(self, collection, id, score):
        collection = self.db[collection]
        collection.update_one({'_id': id}, {"$set": {'score1': score}})

    def addScoreTwo(self, collection, id, score):
        collection = self.db[collection]
        collection.update_one({'_id': id}, {"$set": {'score2': score}})

    def addRelation(self, collection, id, score):
            collection = self.db[collection]
            collection.update_one({'_id': id}, {"$set": {'aggrScore': score}})

    def returnSelectedColAsDf(self, collection):
        collection = self.db[collection]
        data = collection.find({'likes_count': {'$gte': 10}})
        df = pd.DataFrame(list(data))
        return df

    def addEmbedding(self, collection, id, embedding):
            collection = self.db[collection]
            collection.update_one({'_id': id}, {"$set": {'bertEmbedding': embedding}})

    def addClusterInfo(self, collection, id, cInfo):
            collection = self.db[collection]
            collection.update_one({'_id': id}, {"$set": {'clusterInfo': cInfo}})


    #
    #     db.targetCoins.find().forEach(function(data)
    #     {
    #         db.targetCoins.update({
    #             "_id": data._id
    #         }, {
    #             "$set": {
    #                 "likes_count": parseInt(data.likes_count)
    #             }
    #         });
    #     })
    # # #
    #
    #
        # db.storage.updateMany(
        #     {},
        #     [{"$set": {"publishDate": {"$toDate": "$publishDate"}}}]
        # );
    # #
#{'published_date':{$gte:ISODate("2022-05-05"),$lt:ISODate("2020-06-01"}}
