import tensorflow as tf
import numpy as np
from tensorflow import keras

from path import tf_model_path



# 모델 가져오기
def load_model():
    return instantiate_model().model


# 인스턴스 가져오기
def instantiate_model():
    return _SingletonModel.instance()


# MNIST 모델 저장
def save_model():
    (train_images, train_labels), (test_images, test_labels) = tf.keras.datasets.mnist.load_data()

    train_labels = train_labels
    test_labels = test_labels

    train_images = train_images.astype("float32") / 255.0
    test_images = test_images.astype("float32") / 255.0

    train_images = np.expand_dims(train_images, -1)
    test_images = np.expand_dims(test_images, -1)

    # 모델 생성 후 학습
    model = _create_model()
    model.summary()
    model.fit(train_images, train_labels, epochs=20)

    # 주어진 경로에 모델 저장.
    model.save(str(tf_model_path()))


# 모델을 한 번만 생성하기 위해 싱글톤 클래스 사용
class _SingletonModel:
    _instance = None

    @classmethod
    def _get_instance(cls):
        return cls._instance
    
    @classmethod
    def instance(cls, *args, **kwargs):
        cls._instance = cls(*args, **kwargs)
        cls.instance = cls._get_instance
        return cls._instance
    
    def __init__(self):
        self._model = tf.keras.models.load_model(str(tf_model_path()))

    @property
    def model(self):
        return self._model


# MNIST용 간단 모델 생성
def _create_model():
    # model = tf.keras.models.Sequential([
    #     keras.layers.Dense(512, activation="relu", input_shape=(784,)),
    #     keras.layers.Dropout(0.2),
    #     keras.layers.Dense(10, activation="softmax")
    # ])

    model = keras.Sequential(
        [
            keras.Input(shape=(28, 28, 1)),
            keras.layers.Conv2D(32, kernel_size=(3, 3), activation="relu"),
            keras.layers.MaxPooling2D(pool_size=(2, 2)),
            keras.layers.Conv2D(64, kernel_size=(3, 3), activation="relu"),
            keras.layers.MaxPooling2D(pool_size=(2, 2)),
            keras.layers.Flatten(),
            keras.layers.Dropout(0.5),
            keras.layers.Dense(10, activation="softmax"),
        ]
    )

    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model
