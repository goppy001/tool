#!/home/hoge/.pyenv/versions/3.6.5/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.layers.recurrent import LSTM
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
import os
import datetime as dt
import glob
import csv
import math

#変数宣言
filetype = "2014.csv"
pwd = os.getcwd() + "/"
outdir = pwd + "result/"
filepath=pwd + filetype

#データセッの読込
df = pd.read_csv(filepath, encoding="utf-8", usecols=[2,3,4,5,6], engine='python', skipfooter=1)
df = df.dropna()
   
#日付と時刻を合体
#df.index = df.index.map(lambda x: dt.datetime.strptime(df.loc[x].DATE + " " + df.loc[x].TIME, "%Y-%m-%d %H:%M:%S"))

plt.figure()
plt.plot(df)
plt.savefig(outdir + "2014.png")
plt.close('all')

print(df.head())

dataset = df.values
dataset = dataset.astype('float32')


#正規化
scaler = MinMaxScaler(feature_range=(0,1))
dataset = scaler.fit_transform(dataset)

#訓練データとテストデータの仕分け
train_size = int(len(dataset) * 0.8)
test_size  = len(dataset) - train_size
train, test = dataset[0:train_size,:], dataset[train_size:len(dataset),:]
print(len(train), len(test))

#値をずらして配列に格納
def create_dataset(dataset, look_back=1):
    dataX, dataY = [], []
    for i in range(len(dataset)-look_back-1):
        xset = []
        for j in range(dataset.shape[1]):
            a = dataset[i:(i + look_back), j]
            xset.append(a)
        dataX.append(xset)
        dataY.append(dataset[i + look_back, 0])
    return np.array(dataX), np.array(dataY)

#reshape into X=t and Y=t+1
look_back = 31
trainX, trainY = create_dataset(train, look_back)
testX, testY = create_dataset(test, look_back)
print(testX.shape)
print(testX[0])
print(testY)

#LSTMが受け取れるように変換
trainX = np.reshape(trainX, (trainX.shape[0], trainX.shape[1], trainX.shape[2]))
testX = np.reshape(testX, (testX.shape[0], testX.shape[1], testX.shape[2]))

#モデル生成
model = Sequential()
model.add(LSTM(4, input_shape=(testX.shape[1], look_back)))
model.add(Dense(1))
model.compile(loss='mean_squared_error', optimizer='adam')
model.fit(trainX, trainY, epochs=1000, batch_size=1, verbose=2)

#検証
trainPredict = model.predict(trainX)
testPredict = model.predict(testX)
pad_col = np.zeros(dataset.shape[1]-1)
def pad_array(val):
    return np.array([np.insert(pad_col, 0, x) for x in val])

trainPredict = scaler.inverse_transform(pad_array(trainPredict))
trainY = scaler.inverse_transform(pad_array(trainY))
testPredict = scaler.inverse_transform(pad_array(testPredict))
testY = scaler.inverse_transform(pad_array(testY))

#標準偏差算出
trainScore = math.sqrt(mean_squared_error(trainY[:,0], trainPredict[:,0]))
print('train Score: %.2f RMSE' % (trainScore))
testScore = math.sqrt(mean_squared_error(testY[:,0], testPredict[:,0]))
print('Test Score: %.2f RMSE' % (testScore))

print(testY[:,0])
print(testPredict[:,0])

#shift train predictions for plotting
trainPredictPlot = np.empty_like(dataset)
trainPredictPlot[:, :] = np.nan
trainPredictPlot[look_back:len(trainPredict)+look_back, :] = trainPredict

#shift test predictions for plotting 
testPredictPlot = np.empty_like(dataset)
testPredictPlot[:, :] = np.nan
testPredictPlot[len(trainPredict)+(look_back*2)+1:len(dataset)-1, :] = testPredict

# plot baseline and predictions
plot.figure()
plt.plot(scaler.inverse_transform(dataset))
plt.plot(trainPredictPlot)
plt.plot(testPredictPlot)
plt.savefig("outdir" + "2014_result.png")
plt.iclose('all')

#学習データを保存する
model_json_str = model.to_json()
open("2014.json", 'w').write(josn_string)

#重みの保存
model.save_weights("2014.json.h5")
