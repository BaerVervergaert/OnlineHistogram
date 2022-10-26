from main import *
import numpy as np
import pandas as pd
import string

def create_test_data(N,d):
    data = np.random.random(size=(N,d))
    df = pd.DataFrame(data = data, columns = list(string.ascii_letters[:d]))
    return(df)

if __name__=='__main__':
    N, d = 1000, 3
    data = create_test_data(N, d)
    print(data)