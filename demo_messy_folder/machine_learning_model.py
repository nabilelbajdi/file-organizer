#!/usr/bin/env python3
"""
Neural Network for Image Classification
Uses TensorFlow/Keras for deep learning
"""

import tensorflow as tf
from tensorflow import keras
import numpy as np
import matplotlib.pyplot as plt

class ImageClassifier:
    def __init__(self, input_shape=(224, 224, 3), num_classes=10):
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.model = self._build_model()
    
    def _build_model(self):
        model = keras.Sequential([
            keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=self.input_shape),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Conv2D(64, (3, 3), activation='relu'),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Conv2D(64, (3, 3), activation='relu'),
            keras.layers.Flatten(),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(self.num_classes, activation='softmax')
        ])
        return model
    
    def train(self, X_train, y_train, epochs=10, batch_size=32):
        self.model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2
        )
        return history 