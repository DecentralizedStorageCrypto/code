from db import mongodb

localhost = "mongodb://127.0.0.1:27017"
db_name = "players"
mng = mongodb(localhost, db_name)
collection_name_1 = "entitiesV2"

doc = {
    'player': 'Bitcoin News',
    'category': 'infulencer',
    'description': 'infulencer of market',
    'root': 'player',
    'twitter': '@BTCTN',
    'link': ''
}

mng.writeOne(collection_name_1, doc)