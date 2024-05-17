from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
 
file = open("all.txt", "w")
options = Options()
options.add_argument("--headless")
browser = webdriver.Chrome(options=options)
# not showing browser GUI (makes code much faster)
 
def load_index_name(isin):
        url="https://www.justetf.com/it/etf-profile.html?isin=" + isin

        browser.get(url)
 
        # get html of justetf page and look for index name
        html=browser.page_source
        index = html.find("replica l'indice",0) + 16
 
        index_name=""
        letter=''
        # the index name is found before the first . symbol in the text
        while letter!='.':
            index += 1
            try:
                letter = html[index]
            except:
                print("Error")
                time.sleep(180)
                browser.close()
                load_index_name(isin)
                return ""
            if letter != '.':
                index_name+=letter
            if letter == '&':
                index += 4
                
        index = html.find('id="etf-second-id">',1) + 18

        ticker=""
        letter=''
        # the index name is found before the first . symbol in the text
        while letter!='<':
            index += 1
            letter = html[index]
            if letter != '<':
                ticker+=letter
        
        browser.close()
        print(index_name+" ("+ticker+")")
        return index_name+" ("+ticker+")"
 
 
db=pd.read_json('ricerca.json') 
for x in db["ISIN"]:
    print(x)
    file.write(x + ": "+load_index_name(x))
