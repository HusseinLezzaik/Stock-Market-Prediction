import pandas as pd
import numpy as np
from sklearn import preprocessing


def missing_value_handling(data, method='drop'):
    data = pd.DataFrame(data)
    # if any NaN in a row, drop the row
    if method == 'drop':
        data.dropna(axis=0, how='any', inplace=True)
    # fill a NaN with the value of prior row of the same column
    elif method == "ffill":
        data.fillna(method='ffill', inplace=True)
    # fill a NaN with the value of next row of the same column
    elif method == 'bfill':
        data.fillna(method='bfill', inplace=True)
    else:
        # fill NaNs with the average value of this column
        data.fillna(data.mean(), inplace=True)
    return data


def scaling(data, method='minmax'):
    data = np.array(data)
    # transform data to centered and with same scale
    # minmax transform it to range[-1,1]
    if method == 'minmax':
        print("---------Shape is ", data.shape)
        if(np.isinf(data).any()):            
            print("INF VALS")

        if(np.isnan(data).any()):
            print("NAN VALS")
        data = preprocessing.minmax_scale(data, feature_range=(0, 1))
    # normalize transform it to normal distribution
    elif method == 'normalize':
        data[:, 0:-1] = preprocessing.normalize(data[:, 0:-1])
    # scale transform it to zero means and unit std
    else:
        data[:, 0:-1] = preprocessing.scale(data[:, 0:-1])
    return data


def preprocess(data, na_method='drop', scale_method='minmax', test_ratio=None):
    # conclude missing value handling and scale
    data=data.replace([np.inf, -np.inf], np.nan)
    data = scaling(missing_value_handling(data, na_method), scale_method)
    if test_ratio is None:
        X = data[:, 0:-1]
        Y = data[:, -1]
        return X, Y
    # if test_ratio is given, do train_test_split
    else:
        X = data[:, 0:-1]
        Y = data[:, -1]
        test_index = int(len(Y) * test_ratio)
        # return train_test_split(X,Y,test_size=test_ratio, random_state=142)
        x_train = X[:-test_index, :]
        y_train = Y[:-test_index]
        x_test = X[-test_index:, :]
        y_test = Y[-test_index:]
        return x_train, x_test, y_train, y_test