import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # 상위 디렉토리를 path에 추가
from evaluator.metrics import rmse, mae, mse, f1


def test_rmse():
    assert rmse([1, 2, 3], [1, 2, 3]) == 0


def test_mae():
    assert mae([1, 2, 3], [2, 2, 4]) == 2/3


def test_mse():
    assert mse([1, 2], [2, 4]) == ((1-2)**2 + (2-4)**2)/2


def test_f1():
    score = f1([0, 1, 0, 1], [0, 1, 1, 1])
    assert 0 <= score <= 1
