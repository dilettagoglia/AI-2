import pickle
from keras import Input
from keras.utils import to_categorical
from numpy import array
from keras.models import Sequential
from keras.layers import LSTM
from keras.layers import Dense


def split_sequence(sequence, n_steps):
    X, y = list(), list()
    for i in range(len(sequence)):
        # find the end of this pattern
        end_ix = i + n_steps
        # check if we are beyond the sequence
        if end_ix > len(sequence)-1:
            break
        # gather input and output parts of the pattern
        seq_x, seq_y = sequence[i:end_ix], sequence[end_ix]
        X.append(seq_x)
        y.append(seq_y)
    return array(X), array(y)


trainingInstances = open("trainingInstances.pickle", "rb")
dataset = pickle.load(trainingInstances)
dataset_conv = []
#print(dataset)
for i in range(len(dataset)):
    seq = []
    for j in range(len(dataset[i])):
        if dataset[i][j] == (0, 1, 0): #shoot
            seq.append(0)
        elif dataset[i][j] == (0, 0, 1):#move
            seq.append(1)
        elif dataset[i][j] == (0, 0, 0):#non va verso la bandiera
            seq.append(2)
    if len(seq) > 10:
        dataset_conv.append(seq)
dataset = dataset_conv

# sampling delle sequenze (ultime 9 azioni)
new_dataset = []
tmp = []
for i in range(len(dataset)):
    for j in range(len(dataset[i]) - 10, len(dataset[i])):
        tmp.append(dataset[i][j])
    new_dataset.append(tmp)
    tmp = []

data = []
#for i in range (0,10):
for i in range (0, len(new_dataset)):
    data.append(new_dataset[i])
data = array(data)

#data = [[0, 2, 2, 2], [0,2,2,0]]
data = to_categorical(data, num_classes=3)
#print(data)

train = []
label = []
for j in data:
    x, y = split_sequence(j, 6)
    train.append(x)
    label.append(y)

X=array(train)
y = array(label)
n_features = 3
n_steps = None

#print(X.shape)
#print(y.shape)
dim = len(X) * len(X[0])
X = X.reshape((dim, 6, 3))
y = y.reshape(dim, 3)

# define model
model = Sequential()
model.add(LSTM(1, activation='relu', input_shape=(None, n_features)))
model.add(Dense(3))
model.compile(optimizer='adam', loss='mse')
# fit model
model.summary()
model.fit(X, y, epochs=300, verbose=1, validation_split=0.2)

with open('LSTM.pickle', 'wb') as handle:
    pickle.dump(model, handle, protocol=pickle.HIGHEST_PROTOCOL)

# demonstrate prediction
x_input = array([0, 2, 2, 1])
x_input = to_categorical(x_input)
print(x_input)
x_input = x_input.reshape((1, len(x_input), 3))
yhat = model.predict(x_input, verbose=0)
print(yhat)
