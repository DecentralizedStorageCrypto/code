
import numpy as np
from db import mongodb
import pandas as pd
#
localhost = "mongodb://127.0.0.1:27017"
db_name = "players"
collection_name = "newsByEdge"
mng = mongodb(localhost, db_name)

df = mng.returnColAsDf(collection_name)
df.to_json("newsByEdge.json")