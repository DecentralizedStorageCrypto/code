import json
from pymongo import MongoClient

# Making Connection
myclient = MongoClient("mongodb://localhost:27017/")

# database
db = myclient["players"]

Collection = db[""]

# Loading or Opening the json file
with open('.json') as file:
    file_data = json.load(file)

try:
    Collection.insert_many(file_data)
except Exception as e:
    print(str(e))