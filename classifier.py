from tensorflow import keras
import numpy as np
from keras import Input
import matplotlib.pyplot as plt
from keras import layers
from keras.layers import Flatten
import tensorflow as tf
from keras.models import Model
import pandas as pd
import sys

def transformer_encoder(inputs, head_size, num_heads, ff_dim, dropout=0):

    # Normalization and Attention
    x = layers.LayerNormalization(epsilon=1e-6)(inputs)
    x = layers.MultiHeadAttention(
        key_dim=head_size, num_heads=num_heads, dropout=dropout
    )(x, x)
    x = layers.Dropout(dropout)(x)
    res = x + inputs

    # Feed Forward Part
    x = layers.LayerNormalization(epsilon=1e-6)(res)
    x = layers.Conv1D(filters=ff_dim, kernel_size=1, activation="relu")(x)
    x = layers.Dropout(dropout)(x)
    x = layers.Conv1D(filters=inputs.shape[-1], kernel_size=1)(x)
    return x + res

def build_model(head_size,num_heads,ff_dim,num_transformer_blocks,mlp_units,dropout=0,mlp_dropout=0):

    inputs1 = keras.Input(shape=(16, 48))
    x1 = inputs1
    for _ in range(num_transformer_blocks):
        x1 = transformer_encoder(x1, head_size, num_heads, ff_dim, dropout)
    d1 = Flatten()(x1)
    inputs2 = keras.Input(shape=((7, 48)))
    x2 = inputs2
    for _ in range(num_transformer_blocks):
        x2 = transformer_encoder(x2, head_size, num_heads, ff_dim, dropout)
    d2 = Flatten()(x2)
    inputs3 = keras.Input(shape=((7, 92)))
    x3 = inputs3
    for _ in range(num_transformer_blocks):
        x3 = transformer_encoder(x3, head_size, num_heads, ff_dim, dropout)
    d3 = Flatten()(x3)
    x4 = layers.concatenate([d1, d2, d3], axis=-1)
    for dim in mlp_units:
        x4 = layers.Dense(dim, activation="relu")(x4)
        x4 = layers.Dropout(mlp_dropout)(x4)
    outputs = layers.Dense(1, activation="sigmoid")(x4)
    return keras.Model([inputs1, inputs2, inputs3], outputs)

def create_dataset(data1, data2, data3):
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

    for i in range(5):
        y.append(1)

    return np.array(Xe), np.array(Xs), np.array(Xp), np.array(y)

x1 = pd.read_csv("features/filecoin_1.csv")
x2 = pd.read_csv("features/filecoin_2.csv")
x3 = pd.read_csv("features/filecoin_3.csv")

inputs1, inputs2, inputs3, y = create_dataset(x1, x2, x3)

model = build_model(head_size=4, num_heads=2, ff_dim=4, num_transformer_blocks=2, mlp_units=[128],mlp_dropout=0.4,dropout=0.25)

model.compile(
    loss="binary_crossentropy",
    optimizer=keras.optimizers.Adam(learning_rate=1e-4),
    metrics=["accuracy"],
)
model.summary()

callbacks = [keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True)]


model.fit([inputs1, inputs2, inputs3],y, epochs=200,batch_size=64,callbacks=callbacks)