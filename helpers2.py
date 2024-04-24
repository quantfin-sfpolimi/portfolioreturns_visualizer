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

def get_index_data(name):
        try:                
            url = createURL("https://raw.githubusercontent.com/NandayDev/MSCI-Historical-Data/main/countries/", name)
            data = urlopen(url)
        except:
            try:
                url = createURL("https://raw.githubusercontent.com/NandayDev/MSCI-Historical-Data/main/curvo/", name)
                data = urlopen(url)
            except:
                try:
                    url = createURL("https://raw.githubusercontent.com/NandayDev/MSCI-Historical-Data/main/countries_small_cap/", name)
                    data = urlopen(url)
                except:
                    try:
                        url = createURL("https://raw.githubusercontent.com/NandayDev/MSCI-Historical-Data/main/indexes_gross/", name)
                        data = urlopen(url)
                    except:             
                        url = createURL("https://raw.githubusercontent.com/NandayDev/MSCI-Historical-Data/main/regions_small_cap/", name)
                        data = urlopen(url)
        return data

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
    
    portfolio_prices = yf.download(portfolio_tickers)['Open']
    portfolio_prices.dropna(how='any', inplace=True)
    
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
