import requests
from dotenv import load_dotenv
import os
import json
from smtplib import SMTP
from newsapi import NewsApiClient
import time

STOCK = "TSLA"
COMPANY_NAME = "Tesla"
NUMBER_OF_DAYS = 2

load_dotenv()
alpha_api_key = os.getenv("ALPHAVANTAGE_API_KEY")
GOOG_APP_PW = os.getenv("GOOG_APP_PW")
GMAIL_SENDER = os.getenv("GMAIL_SENDER")
GMAIL_RECEIVER = os.getenv("GMAIL_RECEIVER")
NEWS_API = os.getenv("NEWS_API")
ALPHAVANTAGE_URL = "https://www.alphavantage.co/query"
DATA_DIR = "data"
NUMBER_OF_ARTICLES = 3

IS_LOCAL = os.getenv("IS_LOCAL", "false").lower() == "true"

os.makedirs(DATA_DIR,exist_ok=True)

def get_alphavantage_data():
    av_params = {
        "function":"TIME_SERIES_DAILY",
        "symbol": STOCK,
        "apikey":alpha_api_key
                 }
    response = requests.get(ALPHAVANTAGE_URL,params=av_params)

    data = response.json()
    if "Information" in data:
        raise Exception("Rate limit hit with API, using cached data")
    
    if "Time Series (Daily)" not in data:
        raise Exception(f"Unexpected API Response {data}")
    
    data["Time Series (Daily)"] = dict(list(data["Time Series (Daily)"].items())[:NUMBER_OF_DAYS])

    with open(f"{DATA_DIR}/stock_data_file.json", mode="w") as file:
        json.dump(data,file,indent=2)

def get_alphavantage_gq():
    av_params = {
        "function":"GLOBAL_QUOTE",
        "symbol": STOCK,
        "apikey":alpha_api_key
                 }
    
    response = requests.get(ALPHAVANTAGE_URL,params=av_params)
    data = response.json()
    if "Information" in data:
        raise Exception("Rate limit hit with API, using cached data")
    
    if "Global Quote" not in data:
        raise Exception(f"Unexpected API Response {data}")
    
    with open(f"{DATA_DIR}/stock_gq_file.json", mode="w") as file:
        json.dump(data,file,indent=2)

def read_alphavantage_data():
    with open(f"{DATA_DIR}/stock_data_file.json",mode="r") as file:
        data = json.load(file)
    time_series = data["Time Series (Daily)"]
    dates = list(time_series.keys())
    
    prior_close = time_series[dates[1]]["4. close"]
    recent_open = time_series[dates[0]]["1. open"]

    return prior_close, recent_open

def read_alphavantage_gq():
    with open(f"{DATA_DIR}/stock_gq_file.json",mode="r") as file:
        data = json.load(file)
    current_price = (data["Global Quote"]["05. price"])
    return current_price

def calculate_percentages(current, recent, prior):

    recent = float(recent)
    prior = float(prior)
    current = float(current)

    change_close_open = recent-prior
    close_perc = change_close_open/float(prior)*100

    day_change = current-recent
    day_perc = day_change/recent *100

    message = (
        f"Current Price: {current:.2f} \n"
        f"Most Recent Open: {recent} \n"
        f"Prior day close: {prior}\n"
        f"Stock closed at {prior} and opened at {recent} a change of ${change_close_open:.2f} or {close_perc:.2f}%\n"
        f"Stock is currently at {current:.2f} which represents a day change of ${day_change:.2f} or {day_perc:.2f}%\n\n"
    ) 
    
    return message, day_perc, close_perc

def files_exist():
    return os.path.exists(f"{DATA_DIR}/stock_data_file.json") and \
           os.path.exists(f"{DATA_DIR}/stock_gq_file.json")

    

    

def send_email(headlines, percentage_message,day_perc, close_perc):
    domain = "smtp.gmail.com"
    port = 587
    body = percentage_message
    for headline in headlines:
        body += f"Title: {headline[0]}, Description {headline[1]}\n"
    message = f"From: {GMAIL_SENDER}\nTo: {GMAIL_RECEIVER}\nSubject: {STOCK} Ticker Information, Day:{day_perc:.2f}%, Open/Close {close_perc:.2f}%\n\n{body}"


    with SMTP(domain,port=port) as connection:
        connection.starttls()
        connection.login(user=GMAIL_SENDER,password=GOOG_APP_PW)
        connection.sendmail(
            from_addr=GMAIL_SENDER,
            to_addrs=GMAIL_RECEIVER,
            msg=message.encode("utf-8")
        )
    
    print("Successfully sent email")

def access_news():

    newsapi = NewsApiClient(api_key=NEWS_API)
    top_headlines = newsapi.get_everything(q=COMPANY_NAME,
                                              language="en",
                                              sort_by="publishedAt"
                                              )
    articles = (top_headlines["articles"])

    article_result = []

    for article in articles[0:NUMBER_OF_ARTICLES]:
        art_title = article["title"]
        art_descr = article["description"]
        article_result.append((art_title,art_descr))
    return article_result
        


def main():
    print(IS_LOCAL)
    if not IS_LOCAL or not files_exist():
        get_alphavantage_data()
        time.sleep(15)
        get_alphavantage_gq()
    prior_close, recent_open = read_alphavantage_data()
    current_price = read_alphavantage_gq()

    percentage_message,day_perc, close_perc = calculate_percentages(current_price,recent_open,prior_close)

    recent_headlines = access_news()
    send_email(recent_headlines, percentage_message,day_perc,close_perc)

if __name__ == "__main__":
    main()




## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 

## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 


#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

