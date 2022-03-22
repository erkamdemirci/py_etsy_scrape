import glob
import requests
from bs4 import BeautifulSoup
import re
import pygsheets
import pandas as pd
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

max_page = 3
max_product = 150
columnCount = 3

# authorization
now = datetime.datetime.now()
today = datetime.date.today()
someday = datetime.date(2021, 4, 24)
diff = today - someday

gc = pygsheets.authorize(service_file='./creds.json')
sh = gc.open('PRODUCT REVIEWS')

txt_files = glob.glob("*.txt")
print(txt_files)
links = []
for filename in txt_files:
    page = 1
    searchTerm = filename.replace(".txt", "")
    searchTerm = searchTerm[2:]

    try:
        f = open("./products/"+filename, "r")
        text = f.read()
        links = text.split()
    except:
        pass

    while page < max_page+1:
        url = "https://www.etsy.com/search?q=" + \
            searchTerm+"&ref=pagination&page="+str(page)
        req = requests.get(url)
        soup = BeautifulSoup(req.content, 'lxml')

        products = soup.select(
            ".v2-listing-card a.listing-link")
        for shop in products:
            if shop['href'] not in links:
                links.append(shop['href'].split("?ga")[0])
        page += 1

    open("./products/"+filename, 'w').close()
    for link in links:
        f = open("./products/"+filename, "a+")
        f.write(link+"\n")
        f.close()

for filename in txt_files:
    f = open("./products/"+filename, "r")
    text = f.read()
    products = text.split()
    index = filename.split("_")[0]
    wks = sh[int(index)]

    _links = []
    _shops = []
    _reviews = []
    if len(links) > max_product:
        links = links[:max_product]
    for url in links:
        req = requests.get(url)
        soup = BeautifulSoup(req.content, 'lxml')

        title = url.split("/")[-1]
        title = title.replace("-", " ").title()
        link = '=HYPERLINK(CONCATENATE("'+url+'");"'+title+'")'

        shopName = "-"
        try:
            shopName = soup.select("#listing-page-cart a span")[0].text
            shopName = shopName.strip()
        except:
            pass

        try:
            sales = soup.select("#listing-page-cart .wt-text-caption")[0].text
            shopName += " | "+sales
        except:
            pass

        reviews = "-"
        try:
            reviews = soup.select("#same-listing-reviews-tab span")[0].text
            reviews = reviews.strip()
        except:
            pass

        _links.append(link)
        _shops.append(shopName)
        _reviews.append(reviews)

    _links = ['PRODUCT'] + _links
    _shops = ['SHOP NAME'] + _shops
    _reviews = ['REVIEWS'] + _reviews
    d = {'-': _links}
    df = pd.DataFrame(data=d)
    wks.set_dataframe(df, (1, 1))

    d = {'-': _shops}
    df = pd.DataFrame(data=d)
    wks.set_dataframe(df, (1, 2))

    d = {now.strftime("%m/%d/%Y \n  %H:%M"): _reviews}
    df = pd.DataFrame(data=d)
    wks.set_dataframe(df, (1, columnCount))

    print(filename + " - SUCCESS")
