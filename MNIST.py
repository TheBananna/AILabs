# Nicholas Bonanno, pd. 6
import random

import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
import pandas as pd
import time
import random
print('import done')

def ImportPairs(filename):
    training_df = pd.read_csv(filename, header=None)
    inputs = np.array(training_df, dtype=float)
    #inputs = inputs.reshape(-1, 28**2)
    labels = np.array(inputs[:, 0], dtype=int)
    inputs = np.delete(inputs, np.s_[0:1], axis=1)
    inputs = inputs.astype('float32') / 255

    outputs = np.array(list([0] * (labels[i]) + [1] + [0] * (10 - labels[i] - 1) for i in range(len(labels))), dtype=float)
    return inputs, outputs


def GetWeights(dimensions):#I won't be using this because keras can do this for me, but here's it in case you wanted it anyways
    weights = []
    biases = []
    for n, i in enumerate(dimensions[len(dimensions)] - 1):
        weights.append(np.random.rand(i, dimensions[n+1]))
        biases.append(np.random.rand(dimensions[n+1], 1))
    return weights, biases


def WriteModel(model, filename):
    with open(filename, 'w') as file:
        for layer in model.layers:
            layer = layer.get_weights()
            file.write('[' + ','.join(map(str, map(list, layer[0]))) + ']\n')
            file.write('[' + ', '.join(map(str, list(layer[1]))) + ']\n')


model_layer_heights = [784, 392, 196, 98, 49, 10]


model = keras.models.Sequential(
    [layers.InputLayer(input_shape=(784,))] +
    [layers.Dense(model_layer_heights[i], activation='sigmoid') for i in range(1,len(model_layer_heights))]
)


batch_size = 200
epochs = 100
x_train, y_train = ImportPairs('./MNIST/mnist_train.circ')
model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
start = time.time()
model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs)
print(time.time() - start)

WriteModel(model, './MNIST/model.txt')

x_test, y_test = ImportPairs('./MNIST/mnist_test.circ')
print(model.summary())
print('\n\n\n')
print(f'architecture: {model_layer_heights}')
print(f'fast error: {1-model.evaluate(x_test, y_test, verbose=0)[1]}')
error = 0
for i in range(len(x_test)):
    if i % 1000 == 0:
        print(f'test: {i}')
    out = model.predict(x_test[i].reshape(-1, 28**2),verbose=0)#verbosity change added 10/5/2022
    predicted = np.where(out == out.max())[1][0]
    actual = np.where(y_test[i] == y_test[i].max())[0][0]
    if predicted != actual:
        error += 1

error = error/len(x_test)
print(f'real error: {error}')

