import pandas as pd
import yfinance as yf
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_etf_isin(etf_name):
    '''
    Given the etf name, the function outputs its isin by searching for it on the very_long_html.txt file
    Parameters:
        - etf_name: String
    Returns:
        - isin: String
    '''

    with open('very_long_html.txt', 'r') as file:
        data = file.read()

    # NOTA: spesso non trova l'etf a causa di parentesi o altre piccole differenze con justEtf, creare una funzione di ricerca
    #       con gerarchica basata su parole chiave (World, S&P 500, ...) piuttosto che cercare con .find()
    index = data.find(etf_name.upper(),0)

    if index == -1:
        return None

    i=0
    isin=""
    while (i<5):
        index+=1
        letter=data[index]
        if letter == '"':
            i+=1
        if (i>=4) & (letter!='"'):
            isin+=letter

    return isin

def get_index_name(isin):
    '''
    Given the isin of any etf, the function returns the name of the index the ETF tracks.
    The function searches the justEtf page of the given isin on Google Chrome and looks for the underlying index name.
    Parameters:
        - isin: String
    Returns:
        - index_name: String
    '''

    if isin == None:
        return None

    url="https://www.justetf.com/it/etf-profile.html?isin=" + isin

    # not showing browser GUI (makes code much faster)
    options = Options()
    options.add_argument("--headless")
    browser = webdriver.Chrome(options=options)

    browser.get(url);

    # get html of justetf page and look for index name
    html=browser.page_source
    index = html.find("replica l'indice",0) + 16

    index_name=""
    letter=''
    while letter!='.':
        index+=1
        letter=html[index]
        if (letter!='.'):
            index_name+=letter

    return index_name

def get_ter(isin):
    '''
    Given the isin of an ETF, the function returns its ter (in %).
    Parameters:
    - isin: String
    Returns:
    - ter: float
    '''
    if isin == None:
        return 0

    with open('very_long_html.txt', 'r') as file:
        data = file.read() # replace'\n', ''

    index = data.find(isin,0)

    i=0
    ter=""
    while (i<5):
        index+=1
        letter=data[index]
        if letter == '"':
            i+=1
        if (i>=4) & (letter!='"') & (letter!='%'):
            ter+=letter

    return float(ter)


def annual_portfolio_return(portfolio_tickers, portfolio_weight):
    '''
    The function annual_portfolio_return calculates the annual return of 
    a portfolio based on the provided stock symbols and their respective 
    weights. It utilizes historical stock price data downloaded from Yahoo Finance, 
    computes the annual percentage returns for each stock in the portfolio, 
    and then calculates the weighted average portfolio return for each year.
    
    Parameters:
        - portfolio_tickers: string array
            Array containing the tickers of all assets in the portfolio.
        - portfolio_weight: float array
            Array containing the weights of the various stocks.
    Returns:
        - pandas.DataFrame
            DataFrame containing the annual returns (%) of the portfolio with 
            the year as the index and the returns as the only column.
    '''
    
    all_stocks = yf.download(portfolio_tickers)['Open']

    # <-- Giulio: if the ticker is an ETF, look for its underlying index and TER. Add the TERs (of all assets) to TERs list 
    TERs = [0]*len(portfolio_tickers)
    i = 0
    for ticker in portfolio_tickers:
        info = yf.Ticker(ticker).info
        asset_type = info['quoteType']
        if asset_type=="ETF":
            isin = get_etf_isin(info['longName'])
            if isin != None:
                index_name = get_index_name(isin) 
            else:  # sometimes etf name on justetf is abbreviated, sometimes not :/
                isin = get_etf_isin(info['shortName'])
                index_name = get_index_name(isin) 

            TERs[i] = get_ter(isin)
        i+=1

    # you now (hopefully) have the ters and index names of all etfs in the portfolio_tickers list


    portfolio_prices = pd.DataFrame()
    for ticker in portfolio_tickers:
        price = all_stocks[ticker]
        portfolio_prices[ticker] = price

    portfolio_prices.dropna(how='any', inplace=True)
    all_date = list(portfolio_prices.index)
    current_year = int(str(all_date[0])[:4])
    date=[]
    for i in range(0, len(all_date)):
        if current_year == int(str(all_date[i])[:4]):
            date.append(str(all_date[i])[:10])
            current_year+=1
    
    portfolio_year = pd.DataFrame(columns=portfolio_tickers)
    for i in range(0, len(date)):
        portfolio_year.loc[date[i]]=portfolio_prices.loc[date[i]]
    
    stocks_yield = portfolio_year.pct_change().dropna(how='any')
    year_yield=pd.DataFrame(columns=['Yield'])

    for i in range(len(stocks_yield.index)):
        mean_yield=0
        for j in range(len(portfolio_tickers)):
            mean_yield+=stocks_yield.iloc[i][portfolio_tickers[j]]*portfolio_weight[j]
        year_yield.loc[str(date[i])[:4]]=mean_yield*100
    return year_yield

