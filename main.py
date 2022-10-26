import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import bisect

class BaseOnlineHistogramAlgorithm:
    def __init__(self):
        pass
    def loop(self,stream):
        for x in stream:
            self.single_step(x)
    def single_step(self,x):
        x = x
        state = self.find_state(x)
        if self.constraint(state,x):
            self.split(state,x)
        else:
            self.update(state,x)
    def find_state(self,x):
        raise NotImplementedError
    def constraint(self,state,x):
        raise NotImplementedError
    def split(self,state,x):
        raise NotImplementedError
    def update(self,state,x):
        raise NotImplementedError