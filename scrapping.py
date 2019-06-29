import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import csv
import urllib.request
import json
import os
import numpy as np
import re

SAVED_CSV_FILE = 'data/price.csv'
STOCK_LIST_FILE = 'data/stock_list.csv'

class Scrapping:
    def __init__(self):
        print('Instialized scrapping')

    def read_stock_price_page(self, stock_code, page_num):
        '''
        Gets table as dataFrame from Naver stock page
        '''
        target_url = ('http://finance.naver.com/item/sise_day.nhn?code='+ stock_code + '&page=' + str(page_num))
        #print('[INFO] target url: {}'.format(target_url))
        data = pd.read_html(target_url)
        data = data[0]
        data.columns = ['Date', 'Close', 'Diff', 'Open', 'High', 'Low', 'Volume']
        price_data = data.dropna(axis=0, how='any')
        price_data = price_data.drop(price_data.index[0])

        price_data = price_data.reset_index(drop=True)
        price_data['Date'] = pd.to_datetime(price_data['Date'], format='%Y/%m/%d')
        return price_data


    def stock_price_pages_to_df(self, code, days_limit):
        '''
        Pull and add from today to the number of days_limit.
        '''
        print('---code:{}'.format(code))
        df_list_price = []
        page = 1
        while True:  # need to change the code later
            try: 
                data = self.read_stock_price_page(code, page)
                time_limit = dt.datetime.now() - data['Date'][0]
                if time_limit.days > days_limit:
                    print('[INFO] time_limit.day: {}, days_limit: {}'.format(time_limit.days, days_limit))
                    break
                df_list_price.append(data)
                page = page + 1

            except:
                break
        df_price = pd.concat(df_list_price)

        df_price = df_price.reset_index(drop=True)
        # drop unneeded data
        df_price = df_price.drop('Diff', axis=1)
        df_price = df_price.sort_values('Date')

        filename = self.get_data_filename(code)
        df_price.to_csv(filename,index=False)
        print('[INFO] Saved file as {}'.format(filename))


    def show_graph(self, filename=SAVED_CSV_FILE):
        print("Drawing with {}".format(filename))
        try:
            df = pd.read_csv(filename, na_values=["", " ", "-"])
            df = df.reset_index()
            f=df.drop(['index'],axis=1)
        except FileNotFoundError:
            print("File Not Found : " + filename)
            return

        # show as graph
        plt.figure(figsize=(12, 6))
        plt.plot(range(df.shape[0]),(df['Low']+df['High'])/2.0)
        plt.xticks(range(0,df.shape[0],30),df['Date'].loc[::30],rotation=45)
        plt.xlabel('Date',fontsize=18)
        plt.ylabel('Mid Price',fontsize=18)
        # plt.show()
        filename = filename +'_scrapping.png'
        print("saving image as {}".format(filename))
        plt.savefig(filename)

    def find_stock_index(self, company_name):
        try:
            df = pd.read_csv(STOCK_LIST_FILE, na_values=["", " ", "-"])
            df = df.reset_index()
            f=df.drop(['index'],axis=1)
        except FileNotFoundError:
            print("File Not Found : " + filename)
            return

        stock_list = df[['종목코드','기업명']]
        #print(stock_list)

        found_list = stock_list[stock_list['기업명'].str.contains(company_name, na=False)]
        print('[INFO]found_list:{}'.format(found_list))
        ## add error handling code when finding more than one list --> just return the first result
        code = found_list['종목코드']

        print('[INFO]Processing for the companies:\n {}'.format(found_list))
        stock_code=str(list(found_list['종목코드']))
        stock_code=re.sub("\'|\[|\]", "", stock_code).rjust(6,'0')
        print('[INFO]stock_code:{}'.format(stock_code))

        return stock_code

    def get_data_filename(self, stock_code):
        saved_dir = 'data'
        filename = 'price_'
        filename = saved_dir+'/'+filename+stock_code+'.csv'
        print('[INFO]filename:{}'.format(filename))
        return filename


    def generate_report(self, company_name, num_data):
        stock_code = self.find_stock_index(company_name)
        filename = self.get_data_filename(stock_code)
        self.stock_price_pages_to_df(stock_code, num_data)
        self.show_graph(filename)

if __name__ == "__main__":
    scrapping = Scrapping()
    stock_code = '005380'
    days_limit = 2000
    scrapping.generate_report("삼성전기", days_limit)
