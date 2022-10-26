import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import bisect

class StatisticalRecord:
    def __init__(self,name):
        self.name = name

class HistogramRecord(StatisticalRecord):
    def __init__(self,name):
        super(HistogramRecord,self).__init__(self,name)
        self.bins = np.array([-np.inf, np.inf])
        self.count = {}
        self.total_count = 0
    def add_point(self,x):
        self.increment_bins(x)
        self.increment_count(x)
    def increment_bins(self,x):
        pass
    def increment_count(self,x):
        pass

class OnlineHistogram:
    def __init__(self):
        self.records = dict()