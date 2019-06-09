import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, Dropout, LSTM
import matplotlib.pyplot as plt
import tensorflow as tf
from scrapping import Scrapping

scrapping = Scrapping()

SAVED_CSV_FILE = 'data/price.csv'
TRAIN_NUM = 200
PREDICT_NUM = 10
PAST_FOR_PREDICT = 60


def draw_graph(stock_code, new_data, closing_price, num_training):
    plt.figure(figsize=(12, 6))

    train = new_data[:num_training]
    valid = new_data[num_training:]

    valid['Predictions'] = closing_price
    print('[INFO] length of closing_price: {}'.format(len(closing_price)))
    plt.plot(train['Close'])
    print(valid['Predictions'])
    plt.plot(valid[['Close', 'Predictions']])
    plt.xlabel('Date', fontsize=18)
    plt.ylabel('Price', fontsize=18)
    #plt.show()
    filename = scrapping.get_data_filename(stock_code)
    filename = filename+'.png'
    plt.savefig(filename)


def prediction(company_name):
    ## change num_training, past_num, predict_num depending on sampled num of data
    num_training=TRAIN_NUM
    past_num=PAST_FOR_PREDICT
    predict_num=PREDICT_NUM

    stock_code = scrapping.find_stock_index(company_name)
    filename = scrapping.get_data_filename(stock_code)
    df = pd.read_csv(filename, na_values=["", " ", "-"])

    # creating dataframe
    data = df.sort_index(ascending=True, axis=0)
    new_data = pd.DataFrame(index=range(0, len(df)), columns=['Date', 'Close'])
    for i in range(0, len(data)):
        new_data['Date'][i] = data['Date'][i]
        new_data['Close'][i] = data['Close'][i]
    print('[INFO] len(data): {}'.format(len(data)))

    # setting index
    new_data.index = new_data.Date
    new_data.drop('Date', axis=1, inplace=True)

    # creating train and test sets
    dataset = new_data.values

    train = dataset[0:num_training, :]
    valid = dataset[num_training:, :]

    # converting dataset into x_train and y_train
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(dataset)

    x_train, y_train = [], []
    for i in range(past_num, len(train) + predict_num):
        x_train.append(scaled_data[i - past_num: i, 0])
        y_train.append(scaled_data[i, 0])
    x_train, y_train = np.array(x_train), np.array(y_train)

    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

    # create and fit the LSTM network
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
    model.add(LSTM(units=50))
    model.add(Dense(1))

    model.compile(loss='mean_squared_error', optimizer='adam')
    model.fit(x_train, y_train, epochs=1, batch_size=1, verbose=2)

    # predicting 246 values, using past 60 from the train data
    inputs = new_data[len(new_data) - len(valid) - past_num:].values
    print('[INFO] new_data: {}, valid: {}, inputs lengh: {}'.format(len(new_data), len(valid), len(inputs)))

    inputs = inputs.reshape(-1, 1)
    inputs = scaler.transform(inputs)

    X_test = []
    for i in range(past_num, inputs.shape[0]):
        X_test.append(inputs[i - past_num: i, 0])
    X_test = np.array(X_test)

    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
    closing_price = model.predict(X_test)
    closing_price = scaler.inverse_transform(closing_price)

    rms = np.sqrt(np.mean(np.power((valid-closing_price), 2)))

    print('[INFO] rms: {}'.format(rms))

    draw_graph(stock_code, new_data, closing_price, num_training)

# test
scrapping.generate_report('삼성화재')
prediction('삼성화재')
