from fastapi import FastAPI, Path
from pydantic import BaseModel
from typing import Optional
import json


from main import *

app = FastAPI()

@app.get('/')
async def hello_world():
    return {"Msg": "Hello World!"}


@app.get('/search-etf/{isin}/{start_year}/{start_month}/{end_year}/{end_month}')
async def get_seasonality(isin: str, start_year: str, start_month: str, end_year: str, end_month: str):

    start_date = start_year + '-' + start_month + '-' + '01'
    end_date = end_year + '-' + end_month + '-' + '01'
    #etf = yf.Ticker(isin)
    prices = yf.download(isin, interval='1mo', start = start_date, end = end_date)

    return list(prices['Adj Close'])