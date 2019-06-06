import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
import csv
import urllib.request, json
import os
import numpy as np
import tensorflow as tf

SAVED_CSV_FILE = 'data/price.csv'
STOCK_LIST_FILE = 'data/stock_list.csv'

def read_stock_price_page(stock_code, page_num):
    '''
    네이버 주식시세 페이지에 접속하여 table을 dataframe으로 가져와서 정리
    '''
    target_url = ('http://finance.naver.com/item/sise_day.nhn?code='+ stock_code + '&page=' + str(page_num))
    print('[INFO] target url: {}'.format(target_url) )
    data = pd.read_html(target_url)
    data = data[0]
    data.columns = ['Date', 'Close', 'Diff', 'Open', 'High', 'Low', 'Volume']
    price_data = data.dropna(axis=0, how='any')
    price_data = price_data.drop(price_data.index[0])

    price_data = price_data.reset_index(drop=True)
    price_data['Date'] = pd.to_datetime(price_data['Date'], format='%Y/%m/%d')
    return price_data

def stock_price_pages_to_df(code, days_limit=30):
    '''
    오늘부터 days_limit 일수 만큼 이전 날짜 주가를 가져온다.
    '''

    df_list_price = []
    page = 1
    while True:
        try: 
            data = read_stock_price_page(code, page)
            time_limit = dt.datetime.now() - data['Date'][0]
            if time_limit.days > days_limit:
                print('[INFO] time_limit.day: {}, days_limit: {}'.format(time_limit.days, days_limit))
                break
            df_list_price.append(data)
            page = page + 1

        except: break
    df_price = pd.concat(df_list_price)

    df_price = df_price.reset_index(drop=True)
    # drop unneeded data
    df_price = df_price.drop('Diff', axis=1)
    df_price = df_price.sort_values('Date')

    df_price.to_csv(SAVED_CSV_FILE)
    return df_price

def show_graph(filename = SAVED_CSV_FILE):
    try:
        df = pd.read_csv(filename, na_values=["", " ", "-"])
    except FileNotFoundError:
        print("File Not Found : " + filename)
        return

    # show as graph
    plt.figure(figsize = (12,6))
    plt.plot(range(df.shape[0]),(df['Low']+df['High'])/2.0)
    plt.xticks(range(0,df.shape[0],30),df['Date'].loc[::30],rotation=45)
    plt.xlabel('Date',fontsize=18)
    plt.ylabel('Mid Price',fontsize=18)
    plt.show()

def find_stock_index(filename = STOCK_LIST_FILE):
    try:
        df = pd.read_csv(filename, na_values=["", " ", "-"])
    except FileNotFoundError:
        print("File Not Found : " + filename)
        return

    index = '005300'
    print(df)

# Test to get & dave data

stock_code = '005380'
days_limit = 500
df = stock_price_pages_to_df(stock_code, days_limit)
print(df)

#show_graph()