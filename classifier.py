from tensorflow import keras
import numpy as np
from keras import Input
from keras import regularizers
import time
import matplotlib.pyplot as plt
from sklearn.preprocessing import RobustScaler
from keras import layers
from keras.layers import Flatten
from keras.models import Model
import sklearn.metrics as metrics
import pandas as pd
import sys

def transformer_encoder(inputs, head_size, num_heads, ff_dim, dropout=0):

    x = layers.LayerNormalization(epsilon=1e-6)(inputs)
    x = layers.MultiHeadAttention(
        key_dim=head_size, num_heads=num_heads, dropout=dropout
    )(x, x)
    x = layers.Dropout(dropout)(x)
    res = x + inputs
    x = layers.LayerNormalization(epsilon=1e-6)(res)
    x = layers.Conv1D(filters=ff_dim, kernel_size=1, activation="relu")(x)
    x = layers.Dropout(dropout)(x)
    x = layers.Conv1D(filters=inputs.shape[-1], kernel_size=1)(x)
    return x + res

def build_model(head_size,num_heads,ff_dim,num_transformer_blocks,mlp_units,dropout,mlp_dropout):

    input1 = Input(shape=(16, 48), dtype='float32')
    lstm = layers.Bidirectional(layers.LSTM(64, kernel_regularizer=regularizers.l2(0.01)))(input1)
    d1 = layers.Dense(64, kernel_regularizer=regularizers.l2(0.01), activation='relu')(lstm)

    input2 = Input(shape=(7, 48))
    x2 = input2
    for _ in range(num_transformer_blocks[0]):
        x2 = transformer_encoder(x2, head_size[0], num_heads[0], ff_dim, dropout)
    d2 = Flatten()(x2)

    input3 = Input(shape=(7, 92))
    x3 = input3
    for _ in range(num_transformer_blocks[1]):
        x3 = transformer_encoder(x3, head_size[1], num_heads[1], ff_dim, dropout)
    d3 = Flatten()(x3)

    x4 = layers.concatenate([d1, d2, d3], axis=-1)
    for dim in mlp_units:
        x4 = layers.Dense(dim, activation="relu")(x4)
        x4 = layers.Dropout(mlp_dropout)(x4)
    output = layers.Dense(1, activation="sigmoid")(x4)
    return Model([input1, input2, input3], output)

def create_dataset(data1, data2, data3, labels):

    Xe, Xs, Xp, y = [], [], [], []
    e_index = 16
    s_index = 7
    for i in range(0, data1.shape[0], e_index):
        e = data1.iloc[i:i+e_index].values
        Xe.append(e)
    for i in range(0, data2.shape[0], s_index):
        s = data2.iloc[i:i+s_index].values
        Xs.append(s)
    for i in range(0, data3.shape[0], s_index):
        p = data3.iloc[i:i+s_index].values
        Xp.append(p)
    for i in range(labels.shape[0]):
        y.append(labels.iloc[i]['label'])

    return np.array(Xe), np.array(Xs), np.array(Xp), np.array(y)

x1 = pd.read_csv("allData/features-7-1/filecoin_1.csv")
x2 = pd.read_csv("allData/features-7-1/filecoin_2.csv")
x3 = pd.read_csv("allData/features-7-1//filecoin_3.csv")
labels = pd.read_csv("allData/labels-7-1/filecoin.csv")
scaler = RobustScaler()

scale_column_3 = [
'f1','f2','f3','f4','f5','f6','f7','f8','f9','f10',
'f11','f12','f13','f14','f15','f16','f17','f18','f19','f20',
'f21','f22','f23','f24','f25','f26','f27','f28','f29','f30'
,'f31','f32','f33','f34','f35','f36','f37','f38','f39','f40',
'f41','f42','f43','f44','f45','f46','f47','f48','f49','f50',
'f51','f52','f53','f54','f55','f56','f57','f58','f59','f60',
'f61','f62','f63','f64','f65','f66','f67','f68','f69','f70',
'f71','f72','f73','f74','f75','f76','f77','f78','f79','f80'
,'f81','f82','f83','f84','f85','f86','f87','f88','f89','f90',
'f91','f92']

scaler = scaler.fit(x3[scale_column_3])
x3.loc[:, scale_column_3] = scaler.transform(x3[scale_column_3].to_numpy())

Xe, Xs, Xp, y = create_dataset(x1, x2, x3, labels)

input1 = Xe[:, :, :]
input2 = Xs[:, :, :]
input3 = Xp[:, :, :]
train_label = y[0:]
k = 5
num_val_samples = len(input1) // k
num_epochs = 100

head_size = [[6, 23], [8, 46], [12, 23], [6, 46], [12, 46]]
num_heads = [[8, 4], [6, 2], [4, 4], [8, 2], [4, 2]]
ff_dim = [256, 128, 64, 64, 64]
num_transformer_blocks = [[4,4], [4,6], [4,8], [6,8], [8,8]]
mlp_units = [[128], [128, 64], [64, 64], [64, 32], [32, 32]]

for i in range(k):
    print('processing fold #', i)
    input1_val_data = input1[i * num_val_samples: (i + 1) * num_val_samples]
    input2_val_data = input2[i * num_val_samples: (i + 1) * num_val_samples]
    input3_val_data = input3[i * num_val_samples: (i + 1) * num_val_samples]
    val_targets = train_label[i * num_val_samples: (i + 1) * num_val_samples]
    input1_partial_train_data = np.concatenate(
        [input1[:i * num_val_samples],
         input1[(i + 1) * num_val_samples:]],
        axis=0)
    input2_partial_train_data = np.concatenate(
        [input2[:i * num_val_samples],
         input2[(i + 1) * num_val_samples:]],
        axis=0)
    input3_partial_train_data = np.concatenate(
        [input3[:i * num_val_samples],
         input3[(i + 1) * num_val_samples:]],
        axis=0)
    partial_train_targets = np.concatenate(
        [train_label[:i * num_val_samples],
         train_label[(i + 1) * num_val_samples:]],
        axis=0)
    model = build_model(head_size=head_size[1], num_heads=num_heads[1], ff_dim=ff_dim[1],
                        num_transformer_blocks=num_transformer_blocks[1], mlp_units=mlp_units[1],
                        mlp_dropout=0.4, dropout=0.2)
    model.compile(
        loss="binary_crossentropy",optimizer=keras.optimizers.Adam(learning_rate=1e-4),metrics=['accuracy']
    )
    model.summary()
    history = model.fit([input1_partial_train_data, input2_partial_train_data, input3_partial_train_data], partial_train_targets,
              epochs = num_epochs, batch_size=256, validation_data=([input1_val_data, input2_val_data, input3_val_data], val_targets))
    history_dict = history.history
    acc = history.history['accuracy']
    loss_values = history_dict['loss']
    val_loss_values = history_dict['val_loss']
    epochs = range(1, len(acc) + 1)
    plt.plot(epochs, loss_values, 'bo', label='Training loss')
    plt.plot(epochs, val_loss_values, 'b', label='Validation loss')
    plt.title('Training and validation loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.show()
    acc_values = history_dict['accuracy']
    val_acc_values = history_dict['val_accuracy']
    epochs = range(1, len(acc) + 1)
    plt.plot(epochs, acc_values, 'bo', label='Training accuracy')
    plt.plot(epochs, val_acc_values, 'b', label='Validation accuracy')
    plt.title('Training and Validation accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    plt.show()
    # input1_test = Xe[300:, :, :]
    # input2_test = Xs[300:, :]
    # input3_test = Xp[300:, :]
    # test_label = y[300:]
    # test_result = model.evaluate([input1_test, input2_test, input3_test], test_label, verbose=0)
    # preds = model.predict([input1_test, input2_test, input3_test])
    # y_pred = np.where(preds < 0.6, 0, 1)
    # confusion_matrix = metrics.confusion_matrix(test_label, y_pred)
    # print(confusion_matrix)
    # print("Accuracy is: ", metrics.accuracy_score(test_label, y_pred))
    # time.sleep(5)