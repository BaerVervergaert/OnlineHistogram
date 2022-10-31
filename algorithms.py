import numpy as np
from bins import *
from sets import *


class BaseAlgorithm:
    def __init__(self):
        self.count = 0
        self.states = []
    def loop(self,stream):
        for x in stream:
            self.single_step(x)
    def single_step(self,x):
        state = self.find_state(x)
        if self.constraint(state,x):
            self.split(state,x)
        else:
            self.update(state,x)
    def find_state(self,x):
        out = next(filter(lambda state,x=x: x in state,self.states))
        return(out)
    def constraint(self,state,x):
        raise NotImplementedError
    def split(self,state,x):
        raise NotImplementedError
    def update(self,state,x):
        raise NotImplementedError


class BiasVarianceBalancingAlgorithm(BaseAlgorithm):
    def __init__(self,base_width,dim):
        super().__init__()
        self.base_width = base_width
        self.previous_split = 0
        self.dim = dim
        a = [ -np.inf for i in range(self.dim) ]
        b = [ np.inf for i in range(self.dim) ]
        left_inclusive = [ False for i in range(self.dim) ]
        right_inclusive = [ False for i in range(self.dim) ]
        base_set = MultiDimensionalInterval(a,b,left_inclusive,right_inclusive)
        base_bin = HierarchicalBin(base_set,None,0)
        self.states.append(base_bin)
    def constraint(self,state,x):
        if self.count >= 2**(4+self.dim)*self.previous_split/self.base_width:
            return(True)
        else:
            return(False)
    def split(self,state,x):
        new_states = []
        for state in self.states:
            half_bound = [ (state.right_bound[idx] + state.left_bound[idx])/2. for idx in range(state.dim) ]
            new_states.append(state.split(half_bound))
        new_states = tuple(new_states)
        self.states = new_states
    def update(self,state,x):
        raise NotImplementedError
        state.count += 1
        self.count += 1


class HoeffdingLebesgueAlgorithm(BaseAlgorithm):
    def __init__(self,acceptance_rate,dim):
        super().__init__()
        self.acceptance_rate = acceptance_rate
        self.dim = dim
        a = [-np.inf for i in range(self.dim)]
        b = [np.inf for i in range(self.dim)]
        left_inclusive = [False for i in range(self.dim)]
        right_inclusive = [False for i in range(self.dim)]
        base_set = MultiDimensionalInterval(a, b, left_inclusive, right_inclusive)
        base_bin = HierarchicalBin(base_set, None, 0)
        self.states.append(base_bin)
    def constraint(self,state,x):
        t = state.live_count(self.count)
        delta = (state.prob_estimate(self.count)-1/len(self.states))
        if delta>0 and t >= np.log(self.acceptance_rate)*8/(delta**2):
            return(True)
        else:
            return(False)
    def split(self,state,x):
        half_bound = [ (state.right_bound[idx] + state.left_bound[idx])/2. for idx in range(state.dim) ]
        new_states = state.split(half_bound)
        self.states.remove(state)
        self.states += new_states
    def update(self,state,x):
        raise NotImplementedError
        state.count += 1
        self.count += 1
