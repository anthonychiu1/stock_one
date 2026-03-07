import requests
from dotenv import load_dotenv
import os
import json
from smtplib import SMTP

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
NUMBER_OF_DAYS = 2

load_dotenv()
alpha_api_key = os.getenv("ALPHAVANTAGE_API_KEY")
GOOG_APP_PW = os.getenv("GOOG_APP_PW")
GMAIL_SENDER = os.getenv("GMAIL_SENDER")
GMAIL_RECEIVER = os.getenv("GMAIL_RECEIVER")

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

    os.makedirs("data",exist_ok = True)
    with open("data/stock_data_file.json", mode="w") as file:
        json.dump(data,file,indent=2)

def send_email():
    domain = "smtp.gmail.com"
    port = 587
    body="Current price is"
    message = f"From: {GMAIL_SENDER}\nTo: {GMAIL_RECEIVER}\nSubject:{STOCK} Ticker Information\n\n{body}"
    with SMTP(domain,port=port) as connection:
        connection.starttls()
        connection.login(user=GMAIL_SENDER,password=GOOG_APP_PW)
        connection.sendmail(
            from_addr=GMAIL_SENDER,
            to_addrs=GMAIL_RECEIVER,
            msg=message
        )
    
    print("Successfully sent email")
    
get_alphavantage_data()
send_email()


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

