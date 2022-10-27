import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import bisect

class BaseOnlineHistogramAlgorithm:
    def __init__(self):
        self.count = Counter()
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
        raise NotImplementedError
    def constraint(self,state,x):
        raise NotImplementedError
    def split(self,state,x):
        raise NotImplementedError
    def update(self,state,x):
        raise NotImplementedError


class OneDimensionalInterval:
    def __init__(self,
                 left_bound,
                 right_bound,
                 left_bound_inclusive,
                 right_bound_inclusive,
                 ):
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.left_bound_inclusive = left_bound_inclusive
        self.right_bound_inclusive = right_bound_inclusive
    def member(self,x):
        if self.left_bound<x<self.right_bound:
            return(True)
        elif self.left_bound_inclusive and self.left_bound==x:
            return(True)
        elif self.right_bound_inclusive and self.right_bound==x:
            return(True)
        else:
            return(False)
    def size(self):
        out = self.right_bound - self.left_bound
        return(out)
    def __str__(self):
        left_bracket = '[' if self.left_bound_inclusive else '('
        right_bracket = ']' if self.right_bound_inclusive else ')'
        out = f'{left_bracket}{self.left_bound}, {self.right_bound}{right_bracket}'
        return(out)

class NaNSet:
    def __init__(self,qualification):
        self.qualification = qualification
    def member(self,x):
        out = self.qualification(x)
        return(out)

class NaiveOnlineHistogramState(OneDimensionalInterval):
    def __init__(self,*args,parent_state=None,**kwargs):
        super(NaiveOnlineHistogramState,self).__init__(*args,**kwargs)
        self.parent_state = parent_state
        self.count = 0
        if self.parent_state is not None:
            self.latest_count = self.parent_state.latest_count
        else:
            self.latest_count = 0
    def current_estimate_P(self,t):
        if t==0:
            personal_guess = 0.
        else:
            personal_guess = self.count/t
        if self.parent_state is not None:
            parent_count = self.parent_state.latest_count
            out = personal_guess*(self.latest_count-parent_count)/t + .5*self.parent_state.current_estimate_P(t)*parent_count/t
        else:
            out = personal_guess
        return(out)
    def increment(self):
        self.count += 1

class NaNOnlineHistogramState(NaNSet):
    def __init__(self,*args,**kwargs):
        self.count = 0
        self.latest_count = 0
    def current_estimate_P(self,t):
        out = self.count/t
        return(out)
    def increment(self):
        self.count += 1

class Counter:
    def __init__(self):
        self.count = 0
    def increment(self,*args,**kwargs):
        self.count += 1
class NaiveOnlineHistogramAlgorithm(BaseOnlineHistogramAlgorithm):
    def __init__(self):
        super(NaiveOnlineHistogramAlgorithm,self).__init__()
        self._initialize_states()
    def _initialize_states(self):
        self.states = []
        numeric_state = NaiveOnlineHistogramState(-np.inf,np.inf,False,False)
        self.states.append(numeric_state)
        nan_state = NaNSet(np.isnan)
        self.states.append(nan_state)
    def find_state(self,x):
        out = next(filter(lambda state,x=x: state.member(x),self.states))
        return(out)
    def constraint(self,state,x):
        if isinstance(state,OneDimensionalInterval):
            out = state.current_estimate_P(self.count.count) >= (1.+.5)/len(self.states)
            return(out)
        else:
            return(False)
    def split(self,state,x):
        left_bound = state.left_bound
        right_bound = state.right_bound
        if left_bound == -np.inf or right_bound == np.inf:
            half_bound = x
        else:
            half_bound = (left_bound+right_bound)/2.
        if abs(x-left_bound)<abs(x-right_bound):
            left_interval_inclusive = True
            right_interval_inclusive = False
        else:
            left_interval_inclusive = False
            right_interval_inclusive = True
        left_state = NaiveOnlineHistogramState(
            left_bound = left_bound,
            right_bound = half_bound,
            left_bound_inclusive=state.left_bound_inclusive,
            right_bound_inclusive=left_interval_inclusive,
            parent_state=state
        )
        right_state = NaiveOnlineHistogramState(
            left_bound = half_bound,
            right_bound = right_bound,
            left_bound_inclusive=right_interval_inclusive,
            right_bound_inclusive=state.right_bound_inclusive,
            parent_state=state
        )
        self.states.remove(state)
        self.states.append(left_state)
        self.states.append(right_state)
    def update(self,state,x):
        self.count.increment()
        state.increment()
        state.latest_count = self.count.count

class BoundOnlineHistogramAlgorithm(BaseOnlineHistogramAlgorithm):
    def __init__(self,box_bound):
        super(BoundOnlineHistogramAlgorithm,self).__init__()
        self.box_bound = box_bound
        self._initialize_states()
    def _initialize_states(self):
        self.states = []
        numeric_state = NaiveOnlineHistogramState(-np.inf,np.inf,False,False)
        self.states.append(numeric_state)
        nan_state = NaNSet(np.isnan)
        self.states.append(nan_state)
    def find_state(self,x):
        out = next(filter(lambda state,x=x: state.member(x),self.states))
        return(out)
    def constraint(self,state,x):
        if isinstance(state,OneDimensionalInterval):
            out = state.count>=self.box_bound
            return(out)
        else:
            return(False)
    def split(self,state,x):
        left_bound = state.left_bound
        right_bound = state.right_bound
        if left_bound == -np.inf or right_bound == np.inf:
            half_bound = x
        else:
            half_bound = (left_bound+right_bound)/2.
        if abs(x-left_bound)<abs(x-right_bound):
            left_interval_inclusive = True
            right_interval_inclusive = False
        else:
            left_interval_inclusive = False
            right_interval_inclusive = True
        left_state = NaiveOnlineHistogramState(
            left_bound = left_bound,
            right_bound = half_bound,
            left_bound_inclusive=state.left_bound_inclusive,
            right_bound_inclusive=left_interval_inclusive,
            parent_state=state
        )
        right_state = NaiveOnlineHistogramState(
            left_bound = half_bound,
            right_bound = right_bound,
            left_bound_inclusive=right_interval_inclusive,
            right_bound_inclusive=state.right_bound_inclusive,
            parent_state=state
        )
        self.states.remove(state)
        self.states.append(left_state)
        self.states.append(right_state)
    def update(self,state,x):
        self.count.increment()
        state.increment()
        state.latest_count = self.count.count

def plot_onedimensional_algo(left,right,algo):
    def in_bounds(state,left=left,right=right):
        if isinstance(state,OneDimensionalInterval):
            out = state.right_bound>left and state.left_bound<right
        else:
            out = False
        return(out)
    states = [ state for state in algo.states if in_bounds(state)]
    states = sorted(states,key=lambda state:state.left_bound)
    left_bounds = [ state.left_bound for state in states ]
    left_bounds[0] = left
    diff_bounds = [ state.right_bound - state.left_bound for state in states ]
    diff_bounds[0] = left_bounds[1]-left
    diff_bounds[-1] = right-left_bounds[-1]
    height = [ state.current_estimate_P(algo.count.count)/state.size() for state in states ]
    plt.bar(left_bounds,height,diff_bounds,align='edge',linewidth=1,edgecolor='k')
    plt.show()