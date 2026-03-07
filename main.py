import requests
from dotenv import load_dotenv
import os
import json
import smtplib

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
NUMBER_OF_DAYS = 2

load_dotenv()
alpha_api_key = os.getenv("ALPHAVANTAGE_API_KEY")

def get_alphavantage_data():
    av_params = {
        "function":"TIME_SERIES_DAILY",
        "symbol": STOCK,
        "apikey":alpha_api_key
                 }
    alphavantage_url = "https://www.alphavantage.co/query"
    response = requests.get(alphavantage_url,params=av_params)
    data = response.json()
    data["Time Series (Daily)"] = dict(list(data["Time Series (Daily)"].items())[:NUMBER_OF_DAYS])

    with open("stock_data_file.json", mode="w") as file:
        json.dump(data,file,indent=2)

def send_email():
    pass
    
get_alphavantage_data()


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

