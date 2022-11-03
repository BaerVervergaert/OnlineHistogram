class Bin:
    def __init__(self,set):
        super().__init__()
        self.count = 0
        self.set = set
    def __contains__(self, item):
        out = (item in self.set)
        return(out)
    def increment(self,*args,**kwargs):
        self.count += 1
    def live_count(self, current_count):
        live_count = current_count
        return(live_count)
    def prob_estimate(self, current_count):
        live_count = self.live_count(current_count)
        p = self.count/live_count if live_count != 0 else 0.
        return(p)


class HierarchicalBin(Bin):
    def __init__(self,set,parent,birth_count):
        super().__init__(set)
        self.parent = parent
        self.birth_count = birth_count
        self.child_count = 0
    def __str__(self):
        parent_out = str(self.parent)
        parent_out = parent_out.replace('\n','\n\t')
        out = f"{self.count}, {self.set}\n\t{parent_out}"
        return(out)
    def live_count(self, current_count):
        live_count = current_count - self.birth_count
        return(live_count)
    def historical_prob_estimate(self, current_count):
        naive_p = self.prob_estimate(current_count)
        if self.parent is not None:
            parent_birth_count = self.parent.birth_count
            delta = (current_count - self.birth_count) / (current_count - parent_birth_count)
            p = naive_p * delta + (1/self.parent.child_count) * self.parent.historical_prob_estimate(self.birth_count) * (1 - delta)
        else:
            p = naive_p
        return(p)
    def split(self,current_count,*args,**kwargs):
        out = tuple( HierarchicalBin(subset,self,current_count) for subset in self.set.split(*args,**kwargs) )
        self.child_count = len(out)
        return(out)

class MedianHierarchicalBin(HierarchicalBin):
    def __init__(self,step,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.median = None
        self.step = step
    def __str__(self):
        parent_out = str(self.parent)
        parent_out = parent_out.replace('\n','\n\t')
        out = f"{self.count}, {self.birth_count}, {self.median},{self.set}\n\t{parent_out}"
        return(out)
    def increment(self,x,*args,**kwargs):
        x = self.set._check_item_dimension(x)
        self.count += 1
        if self.median is None:
            self.median = x
        else:
            for idx in range(self.set.dim):
                self.median[idx] += self.step/self.count if self.median[idx]<x[idx] else 0.
                self.median[idx] -= self.step/self.count if self.median[idx]>x[idx] else 0.
    def split(self,current_count,*args,**kwargs):
        out = tuple( MedianHierarchicalBin(self.step/2.,subset,self,current_count) for subset in self.set.split(*args,**kwargs) )
        self.child_count = len(out)
        return(out)
