import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import re
import pygsheets
import pandas as pd
import datetime
from random import randint, random
import time

headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
}

# authorization
now = datetime.datetime.now()
today = datetime.date.today()
someday = datetime.date(2021, 4, 24)
diff = today - someday

gc = pygsheets.authorize(service_file='./creds.json')
sh = gc.open('ETSY SALES AND REVIEWS')
wks = sh[0]

shops = ["KELVINUS", "JoyToken", "ExtraStudio", "SoGoodSoWood", "YourWeddingPlace", "Babak1995", "Pegai", "HidesHandcrafted", "YoakumLeather", "HouseLeatherCraft", "ChalcedonCrafts", "MammothLeatherGoods", "VintageRetailCo", "PelleleatherDesign", "GoldenHornWallet", "DiCorio", "HUNmadeStore", "Roarcraft", "GratefulGadgets",
         "BEEngraved", "HeadwallCreative", "DynamicWorkshop", "EngraveMyMemories", "Eatartdrink", "personalizedgiftbox", "BoutiqueHeritage", "CustomSteelandWood", "DSGiftStudio", "WeddingsDecorandMore", "TheTwistedWord", "CopperCloudCreative", "WoodLuckEngraved", "UrartDesign", "BigLemur", "KoiosCrafts", "HeroWoodStand"]

_shops = []
_salesandreviews = []

r = requests.get(
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt")
r_text = r.text
proxies = r_text.split()

random_number = randint(0, len(proxies)-1)
random_proxy = proxies[random_number]
for shop in shops:
    url = "https://www.etsy.com/shop/"+shop
    flag = True
    while flag:
        try:
            http_proxy = "http://"+random_proxy
            https_proxy = "https://"+random_proxy
            ftp_proxy = "ftp://"+random_proxy
            proxyDict = {
                "http": http_proxy,
                "https": https_proxy,
                "ftp": ftp_proxy
            }

            req = requests.get(url, headers=headers,
                               proxies=proxyDict, timeout=3)
            soup = BeautifulSoup(req.content, 'html.parser')

            sales = soup.select(
                ".shop-sales-reviews > .wt-text-caption")[0].getText()
            sales = sales.split(" ")[0]

            link = '=HYPERLINK(CONCATENATE("' + \
                "https://www.etsy.com/shop/"+shop+'");"'+shop+'")'
            reviews = soup.select(
                ".reviews-total .display-inline-block.vertical-align-middle")[-1].getText()
            reviews = re.sub(
                r"([\.\,\\\+\*\?\[\^\]\$\(\)\{\}\!\<\>\|\:\-])", "", reviews)

            _shops.append(link)
            _salesandreviews.append(sales+" | "+reviews)

            print("PROXY SUCCESS -> " + random_proxy)
            flag = False
        except requests.exceptions.ConnectionError:
            r.status_code = "Connection refused"
            del proxies[random_number]
            random_number = randint(0, len(proxies)-1)
            random_proxy = proxies[random_number]
            print("PROXY FAILED -> " + random_proxy)
            time.sleep(5)
            flag = True


_shops = ['Shops'] + _shops
_salesandreviews = ['Sales | Reviews'] + _salesandreviews
d = {'-': _shops}
df = pd.DataFrame(data=d)
wks.set_dataframe(df, (1, 1))

d = {now.strftime("%m/%d/%Y \n  %H:%M"): _salesandreviews}
df = pd.DataFrame(data=d)
wks.set_dataframe(df, (1, diff.days+3))
