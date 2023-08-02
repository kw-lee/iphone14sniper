import math
import cv2
import numpy as np
from scipy import ndimage
import coremltools as ct
from PIL import Image

# 이미지를 읽어서 해당 숫자 리턴.
def get_number_from_image(img, model):
    processed_img = _preprocess_image(img)
    num = _get_num_from_image(img, processed_img)
    out = _predict_digits(num, model)
    return out

def save_image(img, path):
    processed_img = _preprocess_image(img)
    num = _get_num_from_image(img, processed_img)
    Image.fromarray(num).save(path)

# 이미지 전처리
def _preprocess_image(img):
    # 그레이스케일로 변환
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 이진화 처리
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY_INV)[1]
    # gray = cv2.morphologyEx(gray, cv2.MORPH_OPEN, np.ones((2,2)))
    return gray


# 숫자의 이미지만 따오기
def _get_num_from_image(img, preprocessed_img):

    _, labels, stats, centroids = cv2.connectedComponentsWithStats(preprocessed_img)
    img_locations = _get_img_locations_from_stats(stats)

    # 좌표값들 변환
    loc_img = img_locations[0]
    img_x, img_y, img_w, img_h = loc_img.get("x"), loc_img.get("y"), loc_img.get("w"), loc_img.get("h")

    # 이미지 나누기
    img = preprocessed_img[img_y:img_y+img_h, img_x:img_x+img_w]

    # MNIST 이미지들과 동일하게 28x28 이미지로 변환.
    # img = cv2.resize(img, (28, 28), interpolation=cv2.INTER_CUBIC)
    
    # 예측 정확도를 높이기 위해 패딩 적용해서 숫자 가운데 위치
    padded_img = _add_padings(img)

    return padded_img


# 이미지들의 좌표 얻기
def _get_img_locations(contours):
    image_locations = []

    # cnt 순서가 왼쪽->오른쪽 순서로 항상 보장이 되지 않기 때문에 x 좌표값을 체크해서 순서 정해줌.
    for cnt in contours:
        # 찾은 Contour들의 직사각형 그리기
        x, y, w, h = cv2.boundingRect(cnt)
        location = {"x": x, "y": y, "w": w, "h": h}
        # 너무 작은 값은 무시하도록.
        if h >= 8:
            if not image_locations or image_locations[0]["x"] < x:
                image_locations.append(location)
            else:
                image_locations.insert(0, location)
        if len(image_locations) == 2:
            break
    
    return image_locations

# 이미지들의 좌표 얻기
def _get_img_locations_from_stats(stats):
    image_locations = []

    # cnt 순서가 왼쪽->오른쪽 순서로 항상 보장이 되지 않기 때문에 x 좌표값을 체크해서 순서 정해줌.
    for stat in stats[2:]:
        # 찾은 Contour들의 직사각형 그리기
        x, y, w, h, _ = stat
        location = {"x": x, "y": y, "w": w, "h": h}
        # 너무 작은 값은 무시하도록.
        if h >= 8:
            if not image_locations or image_locations[0]["x"] < x:
                image_locations.append(location)
            else:
                image_locations.insert(0, location)
        if len(image_locations) == 2:
            break
    
    return image_locations


# MNIST 이미지 형식에 맞게 이미지에 패딩 추가
def _add_padings(img):
    rows, cols = img.shape
    
    if rows > cols:
        factor = 20.0 / rows
        rows, cols = 20, int(round(cols * factor))
    else:
        factor = 20.0 / cols
        rows, cols = int(round(rows * factor)), 20
    
    img = cv2.resize(img, (cols, rows))
    rows_padding = (int(math.ceil((28 - rows) / 2.0)), int(math.floor((28 - rows) / 2.0)))
    cols_padding = (int(math.ceil((28 - cols) / 2.0)), int(math.floor((28 - cols) / 2.0)))
    img = np.lib.pad(img, (rows_padding, cols_padding), "constant")

    shift_x, shift_y = _get_best_shift(img)
    return _shift(img, shift_x, shift_y)


# 이미지가 이동할 값 리턴
def _get_best_shift(img):
    cy, cx = ndimage.measurements.center_of_mass(img)
    rows, cols = img.shape

    shift_x = np.round(cols/2.0 - cx).astype(int)
    shift_y = np.round(rows/2.0 - cy).astype(int)

    return (shift_x, shift_y)


# 이미지 이동
def _shift(img, shift_x, shift_y):
    rows, cols = img.shape
    M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
    return cv2.warpAffine(img, M, (cols, rows))

def _predict_digits(img, model=None):
    np_img = img.reshape(1, 28, 28, 1).astype("float32") / 255.0
    prediction = model.predict({"input": np_img})["Identity"]
    return np.argmax(prediction, axis=1)

def load_model(model_path):
    model = ct.models.MLModel(model_path)
    return model
