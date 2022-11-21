import newspaper
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time


options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
driver = webdriver.Chrome(executable_path=r'chromedriver/chromedriver.exe', options=options)
driver.maximize_window()
wait = WebDriverWait(driver, 8)
action = webdriver.ActionChains(driver)

#connecting to the mongodb
client = MongoClient("mongodb://127.0.0.1:27017")
#defining database name
db = client["news"]

def collectData():

    driver.get("https://blog.sia.tech/latest")
    time.sleep(1000)
    for counter in range(1000):
        for a in driver.find_elements_by_xpath('/ html / body / div[1] / div[2] / div / div[4] / div / div[1] / div / div / div / div[{counter}] / div / div[3] / a'.format(counter=counter)):
            url = a.get_attribute('href')
            try:
                    news = newspaper.Article(url=url, language='en')
                    news.download()
                    news.parse()
                    # print(news.publish_date)
                    # store the collected news as a json object
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
                        "published_date": news.publish_date,
                        "top_image": str(news.top_image),
                        "link": url
                    }
                    print("->", news)
                    writeToDb(news, "siacoinBlog")
            except:
                    print("this url is not valid ")
                    pass

def writeToDb(news, collection_name):
    collection = db[collection_name]
    collection.insert_one(news)

if __name__=="__main__":
    collectData()