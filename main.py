import requests
import os
from datetime import date, timedelta
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
stock_key = os.environ.get("STOCK_KEY") # the key is saved as an enviroment variable
news_key = os.environ.get("NEWS_KEY") # the key is saved as an enviroment variable

url_stock = "https://www.alphavantage.co/query"
para_stock = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": stock_key,
}
url_news = "https://newsapi.org/v2/everything"
para_news = {
    "qInTitle": COMPANY_NAME,
    "apiKey": news_key
}

account_sid = "# insert your Twilio account sid here"
auth_token = os.environ.get("AUTH_TOKEN") # the key is saved as an enviroment variable
TWILIO_NUMBER = "# insert your twilio account number here (with +country_code)"
YOUR_NUMBER = "# insert your number here (with +country_code)"

# STEP 1: Use https://www.alphavantage.co
r = requests.get(url=url_stock, params=para_stock)
response_stock = r.json()


def get_difference(response: dict):
    today = date.today()
    yesterday = today - timedelta(days=1)
    try:
        stock_close_today = response['Time Series (Daily)'][str(today)]['4. close']
    except KeyError:
        today_new = today - timedelta(days=1)
        yesterday_new = yesterday - timedelta(days=1)
        new_stock_close_today = response['Time Series (Daily)'][str(today_new)]['4. close']
        new_stock_close_yesterday = response['Time Series (Daily)'][str(yesterday_new)]['4. close']
        difference = (float(new_stock_close_today) - float(new_stock_close_yesterday)) * 100 / float(
            new_stock_close_yesterday)
    else:
        stock_close_yesterday = response['Time Series (Daily)'][str(yesterday)]['4. close']
        difference = (float(stock_close_today) - float(stock_close_yesterday)) * 100 / float(stock_close_yesterday)
    return difference



def triangle(number: float):
    if number < 0:
        return "🔻"
    else:
        return "🔺"


stock_dif = round(get_difference(response_stock), 1)
# STEP 2: Use https://newsapi.org
# STEP 3: Use https://www.twilio.com
# If the difference is more than 5%, send the news to your phone as SMS
if abs(stock_dif) >= 5:
    r2 = requests.get(url_news, params=para_news)
    response_news = r2.json()
    three_articles = response_news['articles'][:3]
    news_list = [f"Headline: {news['title']}\nBrief: {news['description']}" for news in three_articles]
    client = Client(account_sid, auth_token)
    for article in news_list:
        message = client.messages \
            .create(
            body=f"{STOCK}: {triangle(stock_dif)}{abs(stock_dif)}%\n{article}",
            from_=TWILIO_NUMBER,
            to=YOUR_NUMBER
        )
