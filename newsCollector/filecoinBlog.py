import xml.etree.ElementTree as ET
import requests
from pymongo import MongoClient
import newspaper

#connecting to the mongodb
client = MongoClient("mongodb://127.0.0.1:27017")
#defining database name
db = client["news"]

#loading the rss page
def loadPage(url, fileName=None):
    flag = False
    # setting the headers of request to get the latest news of rss feed
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    resp = requests.get(url, timeout=20, headers=headers)
    if resp.status_code == 200:
        # saving the xml file
        with open(fileName, 'wb') as f:
            f.write(resp.content)
            f.close()
            flag = True
            return flag
    else:
        return flag

    resp.close()

#parsing xml file
def parseXML(xmlfile, collection_name):
    tree = ET.parse(xmlfile)
    #get root element of xml file
    root = tree.getroot()
    #iterate over news items of xml file
    try:
        for item in root:
            for item in item.findall('item'):
                for child in item:
                    if child.tag == 'link':
                        url = child.text
                    elif child.tag == 'pubDate':
                        publish_date = child.text
                news = newspaper.Article(url=url, language='en')
                news.download()
                news.parse()
                news = {
                    # title : News Headline
                    # text : News content
                    # authors : authors of news
                    # published_date : news timestamp
                    # top_image : related url of top image using in news
                    # link : related url
                    "title": str(news.title),
                    "text": str(news.text),
                    "authors": news.authors,
                    "published_date": publish_date,
                    "top_image": str(news.top_image),
                    "link": url,
                }
                print(news)
                writeToDb(news, collection_name)
    except():
        print("sorry, unable to complete your request")
        pass

#write to the orresponding collection of mongodb
def writeToDb(news, collection_name):
    collection = db[collection_name]
    collection.insert_one(news)

def NewsScrapper():
        #defining the corresponding url
        url = 'https://filecoin.io/blog/feed/index.xml'
        #url = 'https://cointelegraph.com/news/feed/'
        #defining the xml file for gathering the content of feed page
        filename = 'filecoin.xml'
        #filename = 'cointelegraph.xml'
        flag = loadPage(url, filename)
        if flag:
            print('successfully done')
            parseXML(filename, "filecoinBlog")

#calling main to collect latest news of the feed web page
if __name__ == "__main__":
    NewsScrapper()

