# In questo file sfruttiamo gli helper per prendere un portafogli e mandare a javascript i risultati

from helpers_files.helpers import *
from helpers_files.helper2 import *



# Futuri input dell'utente, tramite input dal frontend
tickers = ['SWDA.MI', 'AAPL', 'MSFT']
weights = [0.3, 0.4, 0.3]
start = "2017-01-01"
end = "2020-04-30"
initial_value = 10000


#Calcola la performance del portafoglio

portfolio_performance = portfolio_performance(tickers, weights, start, end, initial_value)

### DA FARE: estratte in un json i prezzi e le date, creare il json e leggerlo da javascript