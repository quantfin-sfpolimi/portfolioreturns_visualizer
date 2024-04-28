# In questo file sfruttiamo gli helper per prendere un portafogli e mandare a javascript i risultati

from helpers_files.helpers import *



# Futuri input dell'utente, tramite input dal frontend
tickers = ['SWDA.MI', 'KO']
weights = [0.5, 0.5]
start = "2000-01-01"
end = "2020-04-30"
initial_amount = 10000.0


stocks_prices = yf.download(tickers, start=start, end=end, interval = '1mo')['Open']

for ticker in stocks_prices.columns:

  if math.isnan(stocks_prices.loc[start, ticker]):
    name = 'iShares Core MSCI World UCITS ETF USD (Acc)'
    isin = get_etf_isin(name)
      
    etf_ter = get_ter(isin)

    print(isin)
    index_name = get_index_name(isin)
    index_prices = get_index_price(index_name, ticker)

    #Sostituisci alla colonna del prezzo le percentuali
    index_prices[ticker] = index_prices[ticker].pct_change()

    index_prices = apply_ter(index_prices, etf_ter, ticker)
    
    # merge

print(index_prices)

