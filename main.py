# In questo file sfruttiamo gli helper per prendere un portafogli e mandare a javascript i risultati

from helpermodules.portfolio_helpers import *
from helpermodules.asset_helpers import *

asset1 = Asset("ETF", "VUAA", "Vanguard S&P 500 UCITS ETF (USD) Accumulating")
asset1.load()

asset2 = Asset("ETF", "EIMI.MI", "iShares Core MSCI Emerging Markets IMI UCITS ETF (Acc)")
asset2.load()
asset2.info()

assets = [asset1, asset2]
portfolio = Portfolio(assets, [0.3, 0.7])

print(portfolio.df)
print(portfolio.portfolio_return_pac(1000, 100, 0.1, True,startdate=startdate, enddate=enddate ))
print(portfolio.monthly_portfolio_return().to_string())

#test