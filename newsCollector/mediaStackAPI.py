import http.client, urllib.parse
import json
from pymongo import MongoClient

#initiating connection to mediastack api
connection = http.client.HTTPConnection('api.mediastack.com')
#initiating connection to mongodb
client = MongoClient("mongodb://127.0.0.1:27017")
#defining database name for storing collected news articles
db = client["StackMedia"]
#defining collection name for storing collected news articles
collection = db["filecoin"]
#defining keyword for searching news articles
keyword = "filecoin"
#defining access key for accessing the api
access_key = 'def5c21a30ad35cda0c1fd7ed7f3961b'

#counting the number of news articles found for the specific keyword and other conditions such as language, technology and etc.
def countNumerOfNews(connection, access_key, keyword):
    #setting the parameters of request
    params = urllib.parse.urlencode({
        'access_key': access_key,
        'keywords': keyword,
        'sort': 'published_desc',
        'languages': 'en',
        'categories': 'technology',
        'limit': 1,
    })
    #making a connection request to api and getting the number of found news articles
    connection.request('GET', '/v1/news?{}'.format(params))
    res = connection.getresponse()
    data = res.read()
    return json.loads(data.decode('utf-8'))['pagination']['total']
#collecting the news articles and strere them to the mongodb
def collectNews(connection, access_key, keyword, totalDoc):
    #defining the limite of news articles that are provided in each page of request
    limit = 100
    remnant = (totalDoc % 100)
    #settting the total number of pages for the requested keyword. each keyword contaons 100 number of newsarticles
    if remnant == 0:
        counter = (totalDoc // 100)
    else:
        counter = (totalDoc // 100) + 1
    for count in range(counter):
        print("offset number-->", count)
        # setting the parameters of request
        params = urllib.parse.urlencode({
            'access_key': access_key,
            'keywords': keyword,
            'sort': 'published_desc',
            'limit': limit,
            'languages': 'en',
            'categories': 'technology',
            'offset': count * limit
        })
        # making a connection request to api and getting the news articles
        connection.request('GET', '/v1/news?{}'.format(params))
        res = connection.getresponse()
        data = res.read()
        writeToDb(data)
#writing the toral number of collected news articles to mongodb, using insrt_many method
def writeToDb(data):

    formatted_data = json.loads(data.decode('utf-8'))['data']
    collection.insert_many(formatted_data)

#calling main function
if __name__ == "__main__":
    totalDoc = countNumerOfNews(connection, access_key, keyword)
    collectNews(connection, access_key, keyword, totalDoc)
