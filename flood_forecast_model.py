# -*- coding: utf-8 -*-
"""flood_train.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1yqmxrWj8pKAntXXBuRvCrKXoiwCiWeua
"""

#importing libraries
import pandas as pd                                             #For manipulating CSV and Tables
import numpy as np                                              #For manipulating matlab style Numpy arrays
import xlrd as xld
import matplotlib.pyplot as plt                                 #For plotting
import seaborn as sns                                           #For visualization tools
import tensorflow as tf                                         #Keras Wrapper with more flexibility
from sklearn.preprocessing import MinMaxScaler                  #For normalization
from tensorflow.keras.models import Sequential                  #Class to set up a simple dense ANN with custom parameters
from tensorflow.keras.layers import Dense, Activation           #Classes that defines the type of network and activation funtions.
from sklearn.metrics import mean_squared_error,mean_absolute_error,explained_variance_score#classes to measure metrics of the network
from tensorflow.keras.callbacks import EarlyStopping

from google.colab import files
uploaded = files.upload()

import io
#data = pd.read_csv('alldata.csv')

# Dataset is now stored in a Pandas Dataframe

#reading the raw data from disk to a dataframe
#data = pd.read_csv('full.csv')
#shuffling the order of rows before test train split
#data = data.sample(frac = 1)

data = pd.read_excel(io.BytesIO(uploaded.get('alldata.xlsx')))

print(data)

#sainity check
data.info();

#data=data.fillna(0)
#data['Rainfall'] = data['Rainfall'].astype(float, errors = 'raise')
#data.info()

#Extracting out raw values of the water level (target of the network) from the table
#WaterL = data[['Water_Level']]
#print(WaterL.shape)
#Extracting out the raw valus of the features from the table
Features = data[['Tmax','Tmin','RH_M','RH_E','Rainfall']]
#sainity Check
Features.head()

#Features= Features.interpolate()
#Features.info()
# WaterL = na_ma(WaterL, k = 2, weighting = "simple")

#x = data['Water_Level'].mean()
#data['Water_Level'].fillna(value= x, inplace= True)
WaterL = data[['Water Level']]

#For Visual Analysis
sns.pairplot(data)
plt.savefig('correlations.png')

#Correlation
data.cov()

#
data.corr()

#instantiating the normalizer
scaler = MinMaxScaler()

#splitting the features into training and testing set
X_train = Features[:1000]
X_test = Features[1000:]
#splitting the target variable dataset into training and testing set
Y_train = WaterL[:1000]
Y_test = WaterL[1000:]
#Normalizing the Features: (X - X.min / X.max - X.min)
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)
#Normalizing the network targets with which we are going to train
Y_train = scaler.fit_transform(Y_train)
Y_test = scaler.transform(Y_test)

#instantiating the keras.model class with a sequential type: multi layer perception
model = Sequential()

#Setting up 5 neurons for the first layer as there are 5 input features to the network with activation sigmoid
model.add(Dense(5,activation='tanh'))
#Adding a Densly connected hidden layer having 10 neurons
model.add(Dense(10,activation='tanh'))
# model.add(Dense(20,activation='tanh'))
# model.add(Dense(40,activation='tanh'))
# model.add(Dense(80,activation='tanh'))
# model.add(Dense(40,activation='tanh'))
# model.add(Dense(20,activation='tanh'))
# model.add(Dense(10,activation='tanh'))

#Final Layer that outputs target variables
model.add(Dense(1))

#The network is compiled and paired with the loss function that is going to be used and optimizing strategy
model.compile(optimizer="adam",loss='mean_squared_error')

#callback function which will be called while training if the validation loss on the test dataset keeps incresing for 25 epochs
early_stop = EarlyStopping(monitor='val_loss',mode='min',verbose=1,patience=25)

#Training the Network More than 100 epochs does not seem to give any substantial improvements in accuracy
model.fit(x=X_train,y=Y_train,epochs=600,validation_data=(X_test,Y_test),callbacks=[early_stop])
#model.fit(X_train,Y_train,epochs=90)

# from ann_visualizer.visualize import ann_viz;

# ann_viz(model, title="model");

#getting the list of losses at the end of each epoch
losses = pd.DataFrame(model.history.history)

#plotting the losses and validation losses as a function of number of epochs trained
losses.plot()
plt.xlabel('number of epochs')
plt.ylabel('validation loss')

#Testing Start
#using the trained network to predict unseen datapoints from the test set.
prediction = model.predict(X_test)
#denormalizing the outputs to proper scale
prediction = scaler.inverse_transform(prediction)
Y_test= scaler.inverse_transform(Y_test)

#Getting the mean absolute error in the test data set
mean_absolute_error(Y_test,prediction)

#saving the model to a .h5 file
model.save("Model_copy1.h5")