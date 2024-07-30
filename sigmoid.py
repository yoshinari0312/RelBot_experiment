import numpy as np


def sigmoid(x):
    return 2.0 / (1.0 + np.exp(-x)) - 1


if __name__ == '__main__':
    print(sigmoid(3))
