# iphone14sniper

딥러닝을 활용해 애플스토어 온라인 홈페이지에서 아이폰 14 제품의 재고가 있으면 자동으로 픽업 구매를 해주는 데모 예제입니다.

## 코드 설명

* `sniping.py`: 애플스토어에서 자동으로 픽업 구매를 해주는 모듈
* `ocr.py`: 카드번호 보안 문자 클릭을 위한 숫자 인식 모듈, 후술할 딥러닝 모형을 사용
* `model`: 간단한 숫자 OCR을 위해 딥러닝 모형 적합
  * MNIST dataset을 기반으로 CNN 모형을 학습
  * 효율을 높이기 위해 Apple의 [Core ML](https://developer.apple.com/machine-learning/core-ml/)을 사용한 형태로 모형 변환
  * 변환한 모형은 `static` 폴더에 저장

## 참고 - OCR 성능

keras로 적합한 모형 사용
```python3
%%timeit -n 100 -r 10
model.predict(np.zeros((2, 28, 28, 1)), verbose=0)
# 20.4 ms ± 514 µs per loop (mean ± std. dev. of 10 runs, 100 loops each)
```

coreml을 사용한 모형 사용
```python3
%%timeit -n 100 -r 10
core_model.predict({"input": np.zeros((2, 28, 28, 1))})
# 508 µs ± 28.8 µs per loop (mean ± std. dev. of 10 runs, 100 loops each)
```

약 40배 정도의 속도 향상을 얻을 수 있음
