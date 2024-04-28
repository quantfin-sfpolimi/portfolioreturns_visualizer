# Libraries used
import datetime as dt
import numpy as np
import os
import pandas as pd
import pickle
import yfinance as yf
from matplotlib import pyplot as plt
import seaborn
import matplotlib.colors
import re
import scipy.stats as ss
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.request import urlopen
from datetime import datetime
import math

history = History()  # Ignore, it helps with model_data function

def download_prices(tickers, start, end, interval='1mo'):
    """
    Download historical stock prices from Yahoo Finance for the specified tickers and time period.

    Parameters:
    tickers: list of str
        List of ticker symbols of the stocks to download prices for.
    start: str or datetime
        Start date of the historical data. Can be a string in 'YYYY-MM-DD' format or a datetime object.
    end: str or datetime
        End date of the historical data. Can be a string in 'YYYY-MM-DD' format or a datetime object.
    interval: str, optional
        Interval for the data. Default is '1mo' (monthly). Other possible values include '1d' (daily),
        '1wk' (weekly), '1mo' (monthly), etc.

    Returns:
    stocks_prices: DataFrame
        DataFrame containing historical stock prices for the specified tickers and time period.
        The columns represent tickers and the rows represent dates.
    """
    stocks_prices = yf.download(tickers, start=start, end=end, interval=interval)['Open']

    return stocks_prices

def portfolio_performance(tickers, weights, start, end, initial_value, interval='1mo'):
    """
    Calculate the performance of a portfolio over a specified time period.

    Parameters:
    tickers: list of str
        List of ticker symbols of the assets in the portfolio.
    weights: list of float
        List of weights corresponding to the assets in the portfolio.
    start: str or datetime
        Start date of the performance analysis period. Can be a string in 'YYYY-MM-DD' format or a datetime object.
    end: str or datetime
        End date of the performance analysis period. Can be a string in 'YYYY-MM-DD' format or a datetime object.
    initial_amount: float
        Initial value of the portfolio.
    interval: str, optional
        Interval for the data. Default is '1mo' (monthly). Other possible values include '1d' (daily),
        '1wk' (weekly), '1mo' (monthly), etc.

    Returns:
    portfolio_performance_df: DataFrame
        DataFrame containing the performance of the portfolio over the specified time period.
        It includes columns for 'Pct Change' (percentage change) and 'Amount' (portfolio value)
        for each date in the analysis period.
    """
    
    # Prendo i prezzi degli assets nel portafoglio
    stocks_pct_change = download_prices(ticker, start, end).pct_change()

    # Prendo le date
    dates = list(stocks_pct_change.index)

    #Creo un dataframe che conterrà cambio percentusale e nuovo valore del portafoglio, data per data
    portfolio_performance_df = pd.DataFrame(columns = ['Pct Change', 'Amount'])

    #Per ogni data, prendi la pct_change pesata per ogni ticker, e mettila nel df Portfolio_pct_change insieme al nuovo valore
    for i in range(len(dates)):
        date = dates[i]
        portfolio_pct_change = 0

        for j in range(len(tickers)):
            ticker = tickers[j]
            weight = weights[j]

            # Prendi la pct change di ogni ticker, pesata, e la sommi a quella totale.
            # Essenzialmente sommatoria per i di pctchange_i é weight_i
            ticker_pct_change = stocks_pct_change.loc[date, ticker]
            weighted_pct_change = ticker_pct_change * weight
            portfolio_pct_change += weighted_pct_change

        portfolio_performance_df.loc[date, 'Pct Change'] = portfolio_pct_change

        if(i == 0):
            # Quando i==0, pct change è Nan e amount è quello iniziale
            amount = initial_amount
        else:
            last_amount = portfolio_performance_df.loc[dates[i-1]]['Amount']
            amount = last_amount + (last_amount * portfolio_pct_change)

        portfolio_performance_df.loc[date]['Amount'] = amount

    return portfolio_performance_df

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

    browser.get(url)

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

def createURL(url, name):
    ''' 
    Given a url and name of an index it creates the correspondant url
    Parameters: url, name (Strings)
    Returns: url (String)
    '''

    for word in name.split():
        if '®' in word:
            word=word[0:-1]

        # & letter cannot be part of a link, %26 to substitute
        if word == "S&P":
            word = "S%26P"

        url += word + "%20"
    return url[:-3] + ".csv"

def get_index_price(name):
        try:                
            url = createURL("https://raw.githubusercontent.com/NandayDev/MSCI-Historical-Data/main/countries/", name)
            price = urlopen(url)
        except:
            try:
                url = createURL("https://raw.githubusercontent.com/NandayDev/MSCI-Historical-Data/main/curvo/", name)
                price = urlopen(url)
            except:
                try:
                    url = createURL("https://raw.githubusercontent.com/NandayDev/MSCI-Historical-Data/main/countries_small_cap/", name)
                    price = urlopen(url)
                except:
                    try:
                        url = createURL("https://raw.githubusercontent.com/NandayDev/MSCI-Historical-Data/main/indexes_gross/", name)
                        price = urlopen(url)
                    except:             
                        url = createURL("https://raw.githubusercontent.com/NandayDev/MSCI-Historical-Data/main/regions_small_cap/", name)
                        price = urlopen(url)
        return price

def get_index_and_etf_data(portfolio_tickers, index_names):
        '''
        Given the portfolio_tickers and index_names lists the function gets the correspondant index name of each ETF.
        Then, it joins the older index data to the newer ETF data month by month, so that we have more historical data
        for ETFs. It returns the portfolio_prices dataframe with the older index data added to it.

        Parameters:
        - portfolio_tickers [List of Strings]
        - index_names [List of Strings]

        Returns:
        - portfolio_prices [Dataframe]
        '''
        portfolio_tickers.append("IBM")
        index_names.append("")
        all_stocks = yf.download(portfolio_tickers, interval='1mo')['Open']
        portfolio_prices = pd.DataFrame()
        for ticker in portfolio_tickers:
            price = all_stocks[ticker]
            portfolio_prices[ticker] = price


        for i in range(0,len(portfolio_tickers)):
            name = index_names[i]
            if name!="":
                data = get_index_data(name)

                ticker = portfolio_tickers[i]
                return_data = pd.read_csv(data, sep=",", names=["Date", ticker], skiprows=1)
                return_data["Date"] += "-01"

                for i in range(0,len(return_data)):
                        return_data.loc[i,"Date"] = datetime.strptime(return_data.loc[i,"Date"], '%Y-%m-%d')

                return_data.set_index("Date", inplace = True)
                portfolio_prices["^"+ticker] = return_data[ticker]
                first_valid_index = portfolio_prices[ticker].index.get_loc(portfolio_prices[ticker].first_valid_index())
                portfolio_prices[ticker].fillna(return_data[ticker]*portfolio_prices[ticker][first_valid_index]/portfolio_prices["^"+ticker][first_valid_index], inplace = True)
                portfolio_prices.drop("^"+ticker, axis=1, inplace = True)
        
        portfolio_prices.drop("IBM", axis=1, inplace = True)
        portfolio_prices.dropna(axis = 0, how = 'all', inplace = True)

        return portfolio_prices

def get_first_date_year(all_date):
    '''
    This function, named get_first_date_year, takes as input a list of 
    dates called all_date. The function returns a list of strings 
    representing the first dates of each year present in the all_date list.
    
    Parameters:
        - all_date: Time_stamp array
            List of dates
    '''
    current_year = int(str(all_date[0])[:4])
    date=[]
    for i in range(0, len(all_date)):
        if current_year == int(str(all_date[i])[:4]):
            date.append(str(all_date[i])[:10])
            current_year+=1
    return date

def annual_portfolio_return(portfolio_prices, portfolio_tickers, portfolio_weight):
    '''
    The function annual_portfolio_return calculates the annual return of 
    a portfolio based on the provided stock symbols and their respective 
    weights. It utilizes historical stock price data downloaded from Yahoo Finance, 
    computes the annual percentage returns for each stock in the portfolio, 
    and then calculates the weighted average portfolio return for each year.
    
    Parameters:
        - portfolio_prices: pandas.DataFrame
            It's a dataframe that contains the opening prices of stocks, 
            with tickers as columns and dates as rows.
        - portfolio_tickers: string array
            Array containing the tickers of all assets in the portfolio.
        - portfolio_weight: float array
            Array containing the weights of the various stocks.
    Returns:
        - pandas.DataFrame
            DataFrame containing the annual returns (%) of the portfolio with 
            the year as the index and the returns as the only column.
    '''
    
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
    
    all_date=(list(portfolio_prices.index))
    date = get_first_date_year(all_date)
    
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
    
def monthly_portfolio_return(portfolio_prices, portfolio_tickers, portfolio_weight):
    '''
    This function outputs a dataframe containing the monthly portfolio return of a list of assets. 
    Parameters:
        - portfolio_prices [Dataframe], containing the monthly(!) value of all assets
        - portfolio_tickers [list of Strings]
        - portfolio_weight [list of floats]
    Returns:
        - month_yield [Dataframe]
    '''

    date=list(portfolio_prices.index)
    stocks_yield = portfolio_prices.pct_change().dropna(how='any')
    month_yield=pd.DataFrame(columns=['Yield'])

    for i in range(len(stocks_yield.index)):
        mean_yield=0
        for j in range(len(portfolio_tickers)):
            mean_yield+=stocks_yield.iloc[i][portfolio_tickers[j]]*portfolio_weight[j]
        month_yield.loc[str(date[i])[:7]]=mean_yield*100
    return month_yield

def portfolio_return_pac(portfolio_prices, portfolio_tickers, portfolio_weight, starting_capital, amount, fee, percentage):
    '''
    The portfolio_return_pac function outputs a Dataframe with the monthly value of a portfolio built using a PAC (Piano di Accumulo di Capitale) strategy.
    The user can input a starting_capital (initial amount of money in the portfolio), the amount of money that he/she invests each month and a broker's fee.
    If the fee is a fixed amount for each new contribution the percentage parameter should be set as False. If the fee is based on a percentage of the
    contribution the percentage parameter should be set as True.
    Parameters:
        - portfolio_prices [Dataframe], containing the monthly(!) value of all assets
        - portfolio_tickers [list of Strings]
        - portfolio_weight [list of floats]
        - starting_capital [int]
        - amount [int]
        - fee [int]
        - percentage [boolean]
    Returns:
        - capital_df [Dataframe]
    '''
    
    month_yield = monthly_portfolio_return(portfolio_prices, portfolio_tickers, portfolio_weight)
    capital = starting_capital
    capital_df = pd.DataFrame(columns=['Capital'])
    date=list(month_yield.index)

    for i in range(len(date)):
        if percentage:
            capital += amount - amount*fee/100
        else:
            capital += amount - fee

        capital += month_yield["Yield"].iloc[i]*capital/100
        capital_df.loc[str(date[i])[:7]] = capital

    return capital_df
    
def portfolio_value(stocks_prices, portfolio_weight):
    '''
        This function, named portfolio_value, calculates the portfolio value 
        for each date present in the stocks_prices dataframe, using the stock 
        prices and portfolio weights provided as input.
        
        Parameters:
            - stocks_prices: pandas.DataFrame
                It's a dataframe that contains the opening prices of stocks, 
                with tickers as columns and dates as rows.
            -portfolio_weight: float array
                Array containing the weights of the various stocks.
        Return:
            - portfolio_prices : Dictionary
                A dictionary containing the portfolio value with corresponding dates as indices.

    '''
    portfolio_prices={}
    for index,row in stocks_prices.iterrows():
        row=list(row)
        price=0
        for i in range(len(row)):
            price+=row[i]*portfolio_weight[i]
            portfolio_prices[str(index.strftime('%Y-%m-%d'))]=price
    return portfolio_prices
    
def graph_plot(portfolio_prices):
    
    '''
        This function, named graph_plot, generates a representative 
        graph of the portfolio values based on the dates provided 
        in the portfolio_prices dictionary.
        
        Parameter:
            - portfolio_prices : Dictionary
                A dictionary containing the portfolio value with corresponding dates as indices.
    '''

    all_date=list(portfolio_prices.keys())
    date=get_first_date_year(all_date)
    date.append(str(all_date[len(all_date)-1])[:10])

    plt.style.use("ggplot")
    plt.plot(list(portfolio_prices.keys()), list(portfolio_prices.values()))
    plt.xticks(date,  rotation=45)
    plt.show()

def MDD(portfolio_prices):
    '''
        This function, named MDD (Maximum Drawdown), calculates the maximum 
        drawdown of a portfolio based on the portfolio prices provided as input.
        
        Parameters:
            - portfolio_prices: Dictionary
                A dictionary containing the portfolio value with corresponding dates as indices.
        
        Return:
            - float
                Maximum Drawdown (%)
    '''
    value=list(portfolio_prices.values())
    return ((max(value)-min(value))/max(value))*100


class PickleHelper:
    def __init__(self, obj):
        self.obj = obj

    def pickle_dump(self, filename):
        """
        Serialize the given object and save it to a file using pickle.

        Parameters:
        obj:
            anything, dataset or ML model
        filename: str
            The name of the file to which the object will be saved. If the filename
            does not end with ".pkl", it will be appended automatically.

        Returns:
        None
        """
        if not re.search("^.*\.pkl$", filename):
            filename += ".pkl"

        file_path = "./pickle_files/" + filename
        with open(file_path, "wb") as f:
            pickle.dump(self.obj, f)

    @staticmethod
    def pickle_load(filename):
        """
        Load a serialized object from a file using pickle.

        Parameters:
        filename: str
            The name of the file from which the object will be loaded. If the filename
            does not end with ".pkl", it will be appended automatically.

        Returns:
        obj: PickleHelper
            A PickleHelper object with the obj loaded from the file accessible through its .obj attribute 
        """
        if not re.search("^.*\.pkl$", filename):
            filename += ".pkl"

        file_path = "./pickle_files/" + filename

        try:
            with open(file_path, "rb") as f:
                pcklHelper = PickleHelper(pickle.load(f))
            return pcklHelper
        except FileNotFoundError:
            print("This file " + file_path + " does not exists")
            return None

    def clean_df(self, percentage, filename):
        """
        Cleans the DataFrame by dropping stocks with NaN values exceeding the given percentage threshold.
        The cleaned DataFrame is pickled after the operation.

        Parameters:
        self
        percentage : float
            Percentage threshold for NaN values. If greater than 1, it's interpreted as a percentage (e.g., 5 for 5%).
        
        Returns:
        None
        """
        if percentage > 1:
            percentage = percentage / 100

        for ticker in self.tickers:
            nan_values = self.dataframe[ticker].isnull().values.any()
            if nan_values:
                count_nan = self.dataframe[ticker].isnull().sum()
                if count_nan > (len(self.dataframe) * percentage):
                    self.dataframe.drop(ticker, axis=1, inplace=True)

        self.dataframe.ffill(axis=1, inplace=True) 
        PickleHelper(obj=self.dataframe).pickle_dump(filename=filename)
