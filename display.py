from matplotlib import pyplot as plt

from sets import OneDimensionalInterval


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
