def fill_with_nan(df, tickers, start_date):
    """
    Create a DataFrame filled with NaN values for the specified tickers from the start_date 
    up to the first available date in the given DataFrame.

    Parameters:
    df: DataFrame
        The DataFrame containing the original data with dates as the index.
    tickers: list of str
        List of ticker symbols.
    start_date: str
        The start date from which to begin filling with NaN values. Format should be 'YYYY-MM'.

    Returns:
    nan_df: DataFrame
        A DataFrame filled with NaN values from the start_date up to the first available date 
        in the original DataFrame. The columns represent the tickers and the index represents the dates.
    """

    first_available_date = list(df.index)[0]
    first_available_year = first_available_date.year
    first_available_month = first_available_date.month

    year = int(start_date[:4])
    month = int(start_date[5:7])

    d = datetime(year, month, 1)
    nan_df = pd.DataFrame(columns = tickers)

    # Crea un df di soli NaN finchè non trovi la data con il primo prezzo
    while (d.year != first_available_year or d.month != first_available_month):
        timestamp = pd.Timestamp(d.year, d.month, 1)
        nan_df.loc[timestamp] = None

        d = datetime(year, month, 1)

        if month + 1 == 13:
            month = 1
            year += 1
        else:
            month += 1

        
    return nan_df
  
  


def find_fundname_by_ticker(ticker, filename='big_file.json'):
    """
    Finds the FUNDNAME for a given TICKER from the JSON data.

    Parameters:
    ticker: str
        The ticker symbol to search for.

    Returns:
    fundname: str or None
        The fund name corresponding to the ticker, or None if not found.
    """

    with open(filename, 'r') as file:
        data = json.load(file)

    
    for entry in data:
        if entry.get('TICKER') == ticker:
            return entry.get('FUNDNAME')

    return None



# TODO: Finish the function
def _merge_single_etf(ticker, startdate, df):

    f = open('big_file.json')
    data = json.load(f)
    fundname = find_fundname_by_ticker(ticker)

    #TODO: Use searchbar/something else to find the right Nanday file for that fundname

    dates = df.index
    for date in dates:
        value = df.loc[date, ticker]
        if value != value: #Se è un NaN
        index_price =



def portfolio_value(tickers, weights, start_date, end_date, initial_amount, recurrent_amount, fees = 0.0):
    # Download data
    df = yf.download(tickers, interval="1mo", start=start_date, end=end_date)['Adj Close']
    
    # Se le prime date non sono disponibili, riempi di NaN quelle date
    if(df.index[0] != start_date):
        nan_df = fill_with_nan(df, tickers, start_date)
        frames = [nan_df, df]
        df = pd.concat(frames)
    
    '''
    TO BE COMPLETED
    for ticker in tickers:
        if df.loc[start_date, ticker] != df.loc[start_date, ticker]:
        if ticker == 'SPY':
            df = _merge_single_etf(ticker, start_date, df)
        #Chiama merge per quel ticker
    '''


    # Useful variables
    shares = {}
    dates = list(df.index)
    startdate = dates[0]

    '''
    *** LUMP SUM ***
    '''
    shares_per_ticker = []
    for i in range(len(tickers)):
        # Calcola il prezzo i-esimo e quindi valuta le shares-iesime da comprare, per ogni ticker nel portafoglio
        price_i = df.loc[startdate, tickers[i]]
        shares_i = ((initial_amount+recurrent_amount) * weights[i]) / price_i
        #Aggiungi le shares i-esime ad un array di dimensione pari al num di tickers
        shares_per_ticker.append(shares_i)

    # L'array delle shares pesate è aggiunto a un dict con corrispondenza data-n° di shares
    shares[startdate] = shares_per_ticker


    '''
    *** DCA ***
    '''
    # Itera lo stesso procedimento del lumpsum ma solo con l'amount mensile, partendo dalla data "startdate + 1"
    dates_without_first_date = list(df.index)[1:]
    for date in dates_without_first_date:
        shares_per_ticker = []
        for i in range(len(tickers)):
        price_i = df.loc[date, tickers[i]]
        shares_i = (recurrent_amount * weights[i]) / price_i
        shares_per_ticker.append(shares_i)

        shares[date] = shares_per_ticker


    '''
    *** CUMULATIVE SHARES PER MONTH ***
    '''
    # Il dict 'shares' contiene le shares acquistate ogni mese, ora calcoliamo la somma cumulativa, ovvero quante shares abbiamo in portafolio mese per mese
    cumulative_shares = {}
    cumulative_shares[startdate] = shares[startdate]
    for date_index in range(1, len(dates)): #Skippa la prima data, è già inserita per evitare complessità.
        cumulative_shares_i = []
        for i in range(len(tickers)):
        cumulative_shares_i.append(shares[dates[date_index]][i] + cumulative_shares[dates[date_index-1]][i]) #Somma l'acquisto i-esimo (primo termine) con la somma cumulativa (secondo termine)

        cumulative_shares[dates[date_index]] = cumulative_shares_i


    '''
    *** PORTFOLIO VALUE ***
    '''
    # Creo un df che, date le shares mese per mese, calcola il valore del portafoglio

    columns = tickers.copy()
    columns.append('Total Portfolio')
    columns.append('Amount spent')
    portfolio_value = pd.DataFrame(columns = columns)

    amount_spent = initial_amount

    for date in dates:
        values_sum = 0
        values = []

        for ticker_i in range(len(tickers)):
        ticker = tickers[ticker_i]
        price = df.loc[date, ticker]
        shares = cumulative_shares[date][ticker_i]

        value = price * shares
        values_sum += value
        values.append(value)


        values.append(values_sum)

        amount_spent += recurrent_amount + fees
        values.append(amount_spent)

        portfolio_value.loc[date] = values

    return portfolio_value