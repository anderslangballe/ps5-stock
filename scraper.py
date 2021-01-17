import bs4 as bs
import urllib.request
import time
import json
import os
import requests
from loguru import logger
from telegram.ext import Updater

updater = Updater(token=os.environ.get('TELEGRAM_TOKEN'), use_context=True)

def send_message(message):
    updater.bot.send_message(os.environ.get('TELEGRAM_CHAT_ID'), message)

send_message('PS5 Scraper Test Message')

def update(product, stock, time, data):
    with open('status.json', 'w') as outfile:
        data[product]['stock'] = stock
        data[product]['time'] = time

        json.dump(data, outfile)


def open_data():
    with open('status.json') as json_file:
        return json.load(json_file)


def filter_html(url, find, identifier):
    soup = bs.BeautifulSoup(requests.get(url).text, 'html.parser')

    return soup.find(find, class_=identifier)


start_time = time.time()
iteration = 0

while True:
    iteration += 1
    logger.info(f'Iteration {iteration}, running for {time.time() - start_time} seconds')
    
    in_stock = []
    data = open_data()
    for product in data:
        url = data[product]['product_url']
        name = data[product]['product_name']
        identifier = data[product]['class']
        store = data[product]['store']
        find = data[product]['find']


        filtered = None
        try:
            filtered = filter_html(url, find, identifier)
        except Exception as e:
            logger.error(e)

            continue

        if store == "Elgiganten" or store == "Proshop" or store == "Happii" or store == "Merlin":
            if filtered is None:
                print("Item available", name, store)
                in_stock.append({'store': store, 'name': name, 'url': url})

        elif store == "Bilka" or store == "Coolshop" or store == "Power" or store =="Foetex" or store == "BR" or store == "Expert":
            if filtered:
                print('Item available', name, store)
                in_stock.append({'store': store, 'name': name, 'url': url})

        time.sleep(1)
    
    if in_stock:
        stores = '\n'.join([f"{stock.get('store')}, {stock.get('name')}: {stock.get('url')}" for stock in in_stock])

        send_message(f'PS5 is in stock!\n{stores}')
