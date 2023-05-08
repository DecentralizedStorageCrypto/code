from tensorflow import keras
import numpy as np
from keras import Input
import matplotlib.pyplot as plt
from keras import layers
from keras.layers import Flatten
from keras.models import Model
import pandas as pd

#this function defines the transformer encoder structure, which includes MultiHeadAttention and conv1d layers
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

#This function builds our classifier model.
def build_model(head_size,num_heads,ff_dim,num_transformer_blocks,mlp_units,dropout,mlp_dropout):

    input1 = Input(shape=(16, 64), dtype='float32')
    conv = layers.Conv1D(filters=256, kernel_size=1, activation="relu")(input1)
    d1 = Flatten()(conv)

    input2 = Input(shape=(14, 32))
    x2 = input2
    for _ in range(num_transformer_blocks[0]):
        x2 = transformer_encoder(x2, head_size[0], num_heads[0], ff_dim, dropout)
    d2 = Flatten()(x2)

    input3 = Input(shape=(14, 80))
    x4 = input3
    for _ in range(num_transformer_blocks[1]):
        x3 = transformer_encoder(x4, head_size[1], num_heads[1], ff_dim, dropout)
    d3 = Flatten()(x3)

    x4 = layers.concatenate([d1, d2, d3], axis=-1)
    for dim in mlp_units:
        x4 = layers.Dense(dim, activation="relu")(x4)
        x4 = layers.Dropout(mlp_dropout)(x4)
    output = layers.Dense(1, activation="sigmoid")(x4)
    return Model([input1, input2, input3], output)

#This function read the input matrices amd create dataset for our model.
def create_dataset(data1, data2, data3, labels):

    Xe, Xs, Xf, y = [], [], [], []
    e_index = 16
    s_index = 14
    f_index = 14
    for i in range(0, data1.shape[0], e_index):
        e = data1.iloc[i:i+e_index].values
        Xe.append(e)

    for i in range(0, data2.shape[0], s_index):
        s = data2.iloc[i:i+s_index].values
        Xs.append(s)

    for i in range(0, data3.shape[0], f_index):
        p = data3.iloc[i:i+f_index].values
        Xf.append(p)
    for i in range(labels.shape[0]):
        y.append(labels.iloc[i]['label'])

    return np.array(Xe), np.array(Xs), np.array(Xf), np.array(y)

if __name__ == "__main__":

    coin_name = input("please enter cryptocurrency name: ")
    x1 = pd.read_csv("allData/features-14-1/{}_1.csv".format(coin_name))
    x2 = pd.read_csv("allData/features-14-1/{}_2.csv".format(coin_name))
    x3 = pd.read_csv("allData/features-14-1/{}_3.csv".format(coin_name))
    labels = pd.read_csv("allData/labels-14-1/{}.csv".format(coin_name))

    Xe, Xs, Xf, y = create_dataset(x1, x2, x3, labels)

    input1 = Xe[:, :, :]
    input2 = Xs[:, :, :]
    input3 = Xf[:, :, :]
    train_label = y[:]

    # define hyper-parameters
    k = 3
    num_val_samples = len(input1) // k
    num_epochs = 200
    head_size = [16, 20]
    num_heads = [2, 4]
    ff_dim = [64]
    num_transformer_blocks = [[4, 8]]
    mlp_units = [64, 64, 64, 64]

    # This block of code includes 3 fold cross-validation, which the average of outputs is used for final classification results.

    for i in range(1, k):
        print('processing fold #', i)
        input1_val_data = input1[i * num_val_samples: (i + 1) * num_val_samples]
        input2_val_data = input2[i * num_val_samples: (i + 1) * num_val_samples]
        input3_val_data = input3[i * num_val_samples: (i + 1) * num_val_samples]
        val_targets = train_label[i * num_val_samples: (i + 1) * num_val_samples]
        input1_partial_train_data = input1[0:i]
        input2_partial_train_data = input2[0:i]
        input3_partial_train_data = input3[0:i]
        partial_train_targets = train_label[0:i]
        model = build_model(head_size=head_size, num_heads=num_heads, ff_dim=ff_dim,
                            num_transformer_blocks=num_transformer_blocks, mlp_units=mlp_units,
                            mlp_dropout=0.2, dropout=0.1)
        model.compile(
            loss="binary_crossentropy", optimizer=keras.optimizers.Adam(learning_rate=1e-4), metrics=['accuracy']
        )
        model.summary()
        history = model.fit([input1_partial_train_data, input2_partial_train_data, input3_partial_train_data,
                             ], partial_train_targets,
                            epochs=num_epochs, batch_size=32, validation_data=(
            [input1_val_data, input2_val_data, input3_val_data], val_targets))
        history_dict = history.history
        acc = history.history['accuracy']
        loss_values = history_dict['loss']
        val_loss_values = history_dict['val_loss']
        epochs = range(1, len(acc) + 1)
        plt.plot(epochs, val_loss_values, 'b', label='Validation loss')
        plt.title('Validation loss')
        plt.xlabel('Epochs')
        plt.ylabel('Loss')
        plt.legend()
        plt.show()
        acc_values = history_dict['accuracy']
        val_acc_values = history_dict['val_accuracy']
        epochs = range(1, len(acc) + 1)
        plt.plot(epochs, val_acc_values, 'b', label='Validation accuracy')
        plt.title('Validation accuracy')
        plt.xlabel('Epochs')
        plt.ylabel('Accuracy')
        plt.legend()
        plt.show()