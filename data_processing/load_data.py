import pandas as pd

def load_rawdata(etf, time_frame):
    file_path = './Data/rawdata/' + etf + '_' + time_frame + '.csv'
    data=""
    try:
        data = pd.read_csv(file_path, index_col=0)
    except  FileNotFoundError:
        print("No such file! Please check your ticker and interval.")
        print("The etf is ", etf)
    return data

def load_svm_modeldata(etf, time_frame):
    file_path = './Data/modeldata/svm_data/' + etf + '_' + time_frame + '_modeldata.csv'
    try:
        data = pd.read_csv(file_path, index_col=0)
    except FileNotFoundError:
        print("No such file! Please check your ticker and interval.")
    return data

def load_ama_modeldata(etf, time_frame):
    file_path = './Data/modeldata/ama_data/' + etf + '_' + time_frame + '_modeldata.csv'
    try:
        data = pd.read_csv(file_path, index_col=0)
    except FileNotFoundError:
        print("No such file! Please check your ticker and interval.")
    return data


