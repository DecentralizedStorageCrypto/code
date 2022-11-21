import newspaper
from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


options = webdriver.ChromeOptions()
# options.add_argument(r"--user-data-dir=C:\\Users\\anup pc\\AppData\\Local\\Google\\Chrome\\User Data") #e.g. C:\Users\You\AppData\Local\Google\Chrome\User Data

#options.add_argument(r"--user-data-dir=C:\\Users\\mansour\\AppData\\Local\Google\\Chrome\\User Data")  # e.g. C:\Users\You\AppData\Local\Google\Chrome\User Data
#options.add_argument(r'--profile-directory=Default')
options.add_argument('--disable-blink-features=AutomationControlled')
# options.add_argument("--incognito")
driver = webdriver.Chrome(executable_path=r'chromedriver/chromedriver.exe')
driver.maximize_window()
action = webdriver.ActionChains(driver)

#connecting to the mongodb
client = MongoClient("mongodb://127.0.0.1:27017")
#defining database name
db = client["news"]
def collectData():

    for page in range(18,19):
        time.sleep(5)
        print("page number is -->", page)
        driver.get("https://www.storj.io/press?2a4da614_page={num}".format(num=page))
        time.sleep(5)
        for a in (driver.find_elements(By.XPATH, '//div[@class="w-dyn-item"]/a')):
            url = a.get_attribute('href')
            print(url)
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
                writeToDb(news, "storjBlog")

            except:
                print("this url is not valid ")
                pass

def writeToDb(news, collection_name):
    collection = db[collection_name]
    collection.insert_one(news)

if __name__=="__main__":
    collectData()