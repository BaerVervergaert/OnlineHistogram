from matplotlib import pyplot as plt

from sets import *


def plot_onedimensional_algo(left,right,algo):
    def in_bounds(state,left=left,right=right):
        if isinstance(state.set,MultiDimensionalInterval):
            out = state.set.right_bound[0]>left and state.set.left_bound[0]<right
        elif isinstance(state.set, OneDimensionalInterval):
            out = state.set.right_bound > left and state.set.left_bound < right
        else:
            out = False
        return(out)
    def singleton(state):
        out = all( lb==rb for lb,rb in zip(state.set.left_bound,state.set.right_bound))
        return(out)
    states = [ state for state in algo.states if in_bounds(state)]
    non_singleton_states = [ state for state in algo.states if not singleton(state)]
    singleton_states = [ state for state in algo.states if singleton(state)]
    non_singleton_states = sorted(non_singleton_states,key=lambda state:state.set.left_bound[0])
    left_bounds = [ state.set.left_bound[0] for state in non_singleton_states ]
    left_bounds[0] = left
    diff_bounds = [ state.set.right_bound[0] - state.set.left_bound[0] for state in non_singleton_states ]
    diff_bounds[0] = left_bounds[1]-left
    diff_bounds[-1] = right-left_bounds[-1]
    height = [ state.historical_prob_estimate(algo.count)/state.set.size() for state in non_singleton_states ]
    height = [ state.prob_estimate(algo.count)/state.set.size() for state in non_singleton_states ]
    print(left_bounds)
    print(diff_bounds)
    print(height)
    print([ state.historical_prob_estimate(algo.count) for state in non_singleton_states ])
    print([ state.prob_estimate(algo.count) for state in non_singleton_states ])
    print([ state.set.size() for state in non_singleton_states ])
    plt.bar(left_bounds,height,diff_bounds,align='edge',linewidth=1,edgecolor='k')
    singleton_x = [ state.set.left_bound for state in singleton_states ]
    singleton_y = [ state.historical_prob_estimate(algo.count) for state in singleton_states ]
    plt.scatter(singleton_x,singleton_y,color='blue',edgecolors='black')
    plt.show()
