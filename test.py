from display import plot_onedimensional_algo
#from main import *
from algorithms import *
import numpy as np
import pandas as pd
import string

def create_test_data(N,d):
    data = np.random.random(size=(N,d))
    df = pd.DataFrame(data = data, columns = list(string.ascii_letters[:d]))
    return(df)

def create_test_data(N,d):
    x = np.zeros(N)
    for i in range(N):
        if np.random.random()<=.5:
            x[i] = np.random.normal(0,1)
        else:
            x[i] = 5.
    data = x
    return(data)

if __name__=='__main__':
    N, d = 10**5, 3
    data = create_test_data(N, d)
    #algo = MedianHoeffdingLebesgueAlgorithm(1.,.1,1)
    algo = BiasVarianceBalancingAlgorithm(2.,1)
    algo.loop(data)
    print('Printing algorithm')
    print(algo)
    print('Plotting')
    plot_onedimensional_algo(-3.,13.,algo)