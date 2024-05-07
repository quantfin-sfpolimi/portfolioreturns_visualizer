import pandas as pd
import yfinance as yf
import seaborn as sns
import re
import matplotlib.pyplot as plt
import yfinance as yf

def download_cpi_data(selected_countries = []):
    """
    Download CPI data from a CSV file and process it.

    Parameters:
        selected_country (list): A list of countries for which CPI data is requested. If provided,
            the function will return CPI data only for the selected countries. If not provided,
            data for all countries will be returned.

    Returns:
        pandas.DataFrame: CPI data for the selected countries (if provided) or for all countries.
    """

    cpi_df = pd.read_csv('Consumer_Price_Index_CPI.csv', delimiter=";")
    cpi_df = cpi_df.rename(columns={'Unnamed: 0': 'Country'})

    # Use years as indexes
    cpi_df = cpi_df.set_index('Country').T

    # Remove Russian data
    cpi_df = cpi_df.drop('Russian Federation', axis=1)

    years = list(cpi_df.index.values)
    countries = list(cpi_df.columns.values)


    # Convert "," to "." in the dataframe    for year in years:
    for country in countries:
        el = str(cpi_df.loc[year].at[country])
        floated_value = float(re.sub(",", ".", el))
        cpi_df = cpi_df.replace(el, floated_value)

    # Return all the dataset or a subset of it
    if selected_countries:
        return cpi_df[selected_countries]
    else:
        return cpi_df