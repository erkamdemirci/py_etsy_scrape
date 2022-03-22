import glob
import requests
from bs4 import BeautifulSoup
import re
import pygsheets
import pandas as pd
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import time

max_page = 3
columnCount = 9

# authorization
now = datetime.datetime.now()
today = datetime.date.today()
someday = datetime.date(2021, 4, 24)
diff = today - someday

gc = pygsheets.authorize(service_file='./creds.json')
sh = gc.open('ETSY CRAWLER')

txt_files = glob.glob("*.txt")
print(txt_files)
shopNames = []
for filename in txt_files:
    page = 1
    searchTerm = filename.replace(".txt", "")
    searchTerm = searchTerm[2:]

    try:
        f = open(filename, "r")
        text = f.read()
        shopNames = text.split()
    except:
        pass

    while page < max_page+1:
        url = "https://www.etsy.com/search?q=" + \
            searchTerm+"&ref=pagination&page="+str(page)
        req = requests.get(url)
        soup = BeautifulSoup(req.content, 'html.parser')

        shops = soup.select(
            ".v2-listing-card__shop")
        for shop in shops:
            try:
                shopName = shop.find("p").text
                if shopName not in shopNames:
                    shopNames.append(shopName)
            except:
                pass

        page += 1

    open(filename, 'w').close()
    for shopName in shopNames:
        f = open(filename, "a+")
        f.write(shopName+"\n")
        f.close()

for filename in txt_files:
    f = open(filename, "r")
    text = f.read()
    shopNames = text.split()
    index = filename.split("_")[0]
    wks = sh[int(index)]

    _shops = []
    _salesandreviews = []
    for shop in shopNames[:150]:
        url = "https://www.etsy.com/shop/"+shop
        req = requests.get(url)
        soup = BeautifulSoup(req.content, 'html.parser')

        sales = "-"
        try:
            sales = soup.select(
                ".shop-sales-reviews > .wt-text-caption")[0].getText()
            sales = sales.split(" ")[0]
        except:
            pass

        link = '=HYPERLINK(CONCATENATE("' + \
            "https://www.etsy.com/shop/"+shop+'");"'+shop+'")'

        reviews = "-"
        try:
            reviews = soup.select(
                ".reviews-total .display-inline-block.vertical-align-middle")[-1].getText()
            reviews = re.sub(
                r"([\.\,\\\+\*\?\[\^\]\$\(\)\{\}\!\<\>\|\:\-])", "", reviews)
        except:
            pass

        _shops.append(link)
        _salesandreviews.append(sales+" | "+reviews)

    _shops = ['Shops'] + _shops
    _salesandreviews = ['Sales | Reviews'] + _salesandreviews
    d = {'-': _shops}
    df = pd.DataFrame(data=d)
    wks.set_dataframe(df, (1, 1))

    d = {now.strftime("%m/%d/%Y \n  %H:%M"): _salesandreviews}
    df = pd.DataFrame(data=d)
    wks.set_dataframe(df, (1, columnCount))
    # wks.set_dataframe(df, (1, diff.days+1))
    print(filename + " - SUCCESS")
