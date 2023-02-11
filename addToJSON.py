import json
from bson.json_util import dumps
import numpy as np
from db import mongodb
import pandas as pd
#
localhost = "mongodb://127.0.0.1:27017"
db_name = "players"
collection_name = "newsByEdge"
mng = mongodb(localhost, db_name)

cursor = mng.returnCorsur(collection_name)
with open('newsByNode.json', 'w') as file:
    json.dump(json.loads(dumps(cursor)), file)
