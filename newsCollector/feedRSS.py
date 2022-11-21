import xml.etree.ElementTree as ET
import requests
from pymongo import MongoClient

#loading the rss page
def loadPage(url, fileName=None):
    flag = False
    # setting the headers of request to get the latest news of rss feed
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
    resp = requests.get(url, timeout=3, headers=headers)
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
def parseXML(xmlfile):
    tree = ET.parse(xmlfile)
    #get root element of xml file
    root = tree.getroot()
    #create empty list to store news items
    newsitems = []
    #iterate over news items of xml file
    for item in root:
        for item in item.findall('item'):
            news = {}
            category = {}
            for child in item:
                if child.tag == 'category':
                    category['item{}'.format(len(category) + 1)] = child.text
                elif child.tag == 'title':
                    news['title'] = child.text
                elif child.tag == 'description':
                    news['description'] = child.text
                elif child.tag == 'pubDate':
                    news['pubDate'] = child.text
                elif child.tag == 'link':
                    news['link'] = child.text

            news['category'] = category
            newsitems.append(news)
    return newsitems

#write to the orresponding collection of mongodb
def writeToDb(data):
    client = MongoClient("mongodb://127.0.0.1:27017")
    db = client["collectedNews"]
    collection = db["newsbtc"]
    collection.insert_many(data)

def NewsScrapper():
        #defining the corresponding url
        url = 'https://www.newsbtc.com/feed/'
        #url = 'https://cointelegraph.com/news/feed/'
        #defining the xml file for gathering the content of feed page
        filename = 'newsbtc.xml'
        #filename = 'cointelegraph.xml'
        flag = loadPage(url, filename)
        if flag:
            print('successfully done')
            data = parseXML(filename)
            print(data)
            writeToDb(data)

#calling main to collect latest news of the feed web page
if __name__ == "__main__":
    NewsScrapper()

