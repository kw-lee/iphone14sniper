import tensorflow as tf
import numpy as np
from tensorflow import keras
import glob
# from path import tf_ft_model_path
# from mnist import load_model

# MNIST 모델 저장
def main():
    train_images = []
    train_labels = []
    for i in range(10):
        path = f"finetune/inicis/{i}.png"
        img = keras.preprocessing.image.load_img(path,
            grayscale=True,
            target_size=(28, 28))
        img = keras.preprocessing.image.img_to_array(img)
        img = np.expand_dims(img, axis=0)
        train_images.append(img)
        train_labels.append(i)

    train_images = np.concatenate(train_images, axis=0)
    train_labels = np.asarray(train_labels)
    train_images = train_images.astype("float32") / 255.0
    train_images = np.expand_dims(train_images, -1)

    # 모델 생성 후 학습
    model = tf.keras.models.load_model("./static/mnist_ft.bin")
    model.summary()
    model.fit(train_images, train_labels, epochs=100)

    # 주어진 경로에 모델 저장.
    model.save("./static/mnist_inicis.bin")

if __name__ == "__main__":
    main()