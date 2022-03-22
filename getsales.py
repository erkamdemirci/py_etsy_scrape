import requests
from bs4 import BeautifulSoup
import re
import pygsheets
import pandas as pd
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

columnCount = 9

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
for shop in shops:
    url = "https://www.etsy.com/shop/"+shop
    req = requests.get(url)
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

_shops = ['Shops'] + _shops
_salesandreviews = ['Sales | Reviews'] + _salesandreviews
d = {'-': _shops}
df = pd.DataFrame(data=d)
wks.set_dataframe(df, (1, 1))

d = {now.strftime("%m/%d/%Y \n  %H:%M"): _salesandreviews}
df = pd.DataFrame(data=d)
# wks.set_dataframe(df, (1, diff.days+2))
wks.set_dataframe(df, (1, columnCount))
