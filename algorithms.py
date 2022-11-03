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
    def __str__(self):
        out = '\n'.join([ str(state) for state in self.states ])
        return(out)


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
        if state.live_count(self.count) == 0:
            return(False)
        if self.count >= 2**(3+self.dim)*self.previous_split/self.base_width:
            return(True)
        return(False)
    def determine_split_point(self,left_bound,right_bound,x):
        l_finite = np.isfinite(left_bound)
        r_finite = np.isfinite(right_bound)
        if l_finite and r_finite:
            split_point = (left_bound + right_bound) / 2.

        elif (not l_finite) and r_finite:
            if left_bound<x<right_bound:
                split_point = x
            else:
                split_point = right_bound-self.base_width

        elif l_finite and (not r_finite):
            if left_bound<x<right_bound:
                split_point = x
            else:
                split_point = left_bound+self.base_width

        elif (not l_finite) and (not r_finite):
            split_point = x
        return(split_point)

    def split(self,_state,x):
        new_states = []
        for state in self.states:
            x = state.set._check_item_dimension(x)
            half_bound = [self.determine_split_point(state.set.left_bound[idx],state.set.right_bound[idx],x[idx]) for idx in range(state.set.dim)]
            half_include = [abs(state.set.left_bound[idx] - x[idx]) <= abs(state.set.right_bound[idx] - x[idx]) for idx in range(state.set.dim)]
            new_states += state.split(self.count, half_bound, half_include)
        new_states = tuple(new_states)
        self.states = new_states
        self.previous_split = self.count
    def update(self,state,x):
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
        if t==0:
            return(False)
        if t==1:
            return(True)
        delta = (state.prob_estimate(self.count)-1/len(self.states))
        if state.live_count(self.count)>0 and delta>0 and t >= np.log(1./self.acceptance_rate)*8/(delta**2):
            return(True)
        return(False)
    def split(self,state,x):
        x = state.set._check_item_dimension(x)
        half_bound = [ (state.set.right_bound[idx] + state.set.left_bound[idx])/2. for idx in range(state.set.dim) ]
        half_bound = [ half_bound[idx] if np.isfinite(half_bound[idx]) else x[idx] for idx in range(state.set.dim) ]
        half_include = [ abs(state.set.left_bound[idx]-x[idx])<=abs(state.set.right_bound[idx]-x[idx]) for idx in range(state.set.dim) ]
        new_states = state.split(self.count,half_bound,half_include)
        self.states.remove(state)
        self.states += new_states
    def update(self,state,x):
        state.count += 1
        self.count += 1
    def __str__(self):
        out = 'HoeffdingLebesgueAlgorithm, with states:\n'
        out += super().__str__()
        return(out)
