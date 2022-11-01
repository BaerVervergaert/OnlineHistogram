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
    states = [ state for state in algo.states if in_bounds(state)]
    states = sorted(states,key=lambda state:state.set.left_bound[0])
    left_bounds = [ state.set.left_bound[0] for state in states ]
    left_bounds[0] = left
    diff_bounds = [ state.set.right_bound[0] - state.set.left_bound[0] for state in states ]
    diff_bounds[0] = left_bounds[1]-left
    diff_bounds[-1] = right-left_bounds[-1]
    height = [ state.current_estimate_P(algo.count.count)/state.size() for state in states ]
    plt.bar(left_bounds,height,diff_bounds,align='edge',linewidth=1,edgecolor='k')
    plt.show()
