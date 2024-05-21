# In questo file sfruttiamo gli helper per prendere un portafogli e mandare a javascript i risultati

from helpermodules.portfolio_helpers import *
from helpermodules.asset_helpers import *

asset1 = Asset("ETF", "VUAA.MI", "Vanguard S&P 500 UCITS ETF (USD) Accumulating")
asset1.index_name = 'S&P 500'
asset1.isin = 'IE00BFMXXD54'
asset1.ter = 0.07
asset1.load_df()

asset2 = Asset("ETF", "EIMI.MI", "MSCI Emerging Markets IMI")
asset2.index_name = 'MSCI Emerging Markets'
asset2.isin = 'IE00BKM4GZ66'
asset2.ter = 0.18
asset2.load_df()


assets = [asset1, asset2]
weights = [1.0, 0.0]
portfolio = Portfolio(assets, weights)


#print(portfolio.df)
print(portfolio.portfolio_return_pac(1000, 0, 0, True, startdate="2020-01-01", enddate="2022-01-01"))
#print(portfolio.monthly_portfolio_return().to_string())
#print(portfolio.graph_returns_frequency())
