import pickle
from math import sqrt

import numpy as np
from numpy import concatenate
from numpy import transpose
import pandas as pd
import matplotlib.pyplot as plt

import tensorflow as tf
from tensorflow.keras import layers, losses, optimizers

from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error

from keras.utils.data_utils import get_file
from keras.callbacks import LambdaCallback
from keras.callbacks import TensorBoard
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import CuDNNLSTM
from keras.layers import LSTM
from keras.layers import Dropout, Softmax
from keras.optimizers import RMSprop, SGD
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

''' DATASET SPLITTING '''

trainingInstances = open("trainingInstances.pickle", "rb")

dataset = pickle.load(trainingInstances)

train = dataset[0:90]  
test = dataset[91:124]  

train1 = []
test1 = []

for t in train:
    instance = []
    for action in t:
        seq = [action[0], action[1], action[2]]
        instance.append(seq)
    train1.append(instance)

for t in test:
    instance = []
    for action in t:
        seq = [action[0], action[1], action[2]]
        instance.append(seq)
    test1.append(instance)

train1 = np.array([np.array(xi) for xi in train1])
test1 = np.array([np.array(xi) for xi in test1])

#  train_size = int(len(dataset) * 0.80)
# test_size = len(dataset) - train_size
# train1, test1 = dt[0:train_size,:], dt[train_size:len(dt),:]

'''
Feeding a NN withs strings/text is not possible. You have to encode them into numbers. 
To carry out this operation different approaches are available.
Used Tokenizer from TF which can help in the process of numerical encoding of text sequences
'''

''' TOKENIZER'''


def create_dataset(dataset, look_back=1):
    X, Y = [], []
    for i in range(len(dataset)-look_back-1):
        a = dataset[i:(i+look_back)]
        X.append(a)
        Y.append(dataset[i + look_back])
    return np.array(X, dtype=np.int), np.array(Y, dtype=np.int)

# DATASET SPLITTING 
  
look_back = 5
X_train, Y_train = create_dataset(train1, look_back)
X_test, Y_test = create_dataset(test1, look_back)



print('\nBefore reshaping:', X_train.shape, Y_train.shape, X_test.shape, Y_test.shape)
print("xtrain : " + str((X_train[1])))
print("ytrain : " + str((Y_train[1])))


# reshape input to be [samples, time steps, features]
X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
X_test = np.reshape(X_test, (X_test.shape[0], 1, X_test.shape[1]))

print('\nAfter reshaping:', X_train.shape, Y_train.shape, X_test.shape, Y_test.shape)

# HYPERPARAM
learning_rate=1e-4
batch_size=70
epochs=20


# BUILDING THE MODEL 
#ok
# using Sequential API
model = tf.keras.Sequential()   # model using Sequential class 
                                # --> will construct a pipeline of layers                         
model.add(layers.LSTM(1, input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(layers.Dropout(0.2))
model.add(layers.Dense(1))
#model.compile(loss='mean_squared_error', optimizer='adam')
model.compile(optimizer='adam',  # try also adam
              loss='mae')




# MODEL FIT 
# fit model
history = model.fit(X_train, Y_train, epochs=epochs, batch_size=batch_size, validation_data=(X_test, Y_test),
                     verbose=1, shuffle=False)
model.summary()
# Plot Model Loss 
# list all data in history
print(history.history.keys())

# summarize history for loss
plt.figure(3)
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss']) #RAISE ERROR
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()

# MODEL PREDICTION 

# make predictions

train_predict = model.predict(X_train)
test_predict = model.predict(X_test)




print('Train Mean Absolute Error:', mean_absolute_error(Y_train[0], train_predict[:,0]))
print('Train Root Mean Squared Error:',np.sqrt(mean_squared_error(Y_train[0], train_predict[:,0])))
print('Test Mean Absolute Error:', mean_absolute_error(Y_test[0], test_predict[:,0]))
print('Test Root Mean Squared Error:',np.sqrt(mean_squared_error(Y_test[0], test_predict[:,0])))


aa=[x for x in range(500)]
plt.figure(figsize=(8,4))
plt.plot(aa, Y_test[0][:500], marker='.', label="actual")
plt.plot(aa, test_predict[:,0][:500], 'r', label="prediction")
# plt.tick_params(left=False, labelleft=True) #remove ticks
plt.tight_layout()
plt.subplots_adjust(left=0.07)
plt.ylabel('Global_active_power', size=15)
plt.xlabel('Time step', size=15)
plt.legend(fontsize=15)
plt.show();

