import itertools


class Set:
    pass


class CategoricalSet(Set):
    def __init__(self,category_members):
        super().__init__()
        self.category_members = category_members
    def __contains__(self, item):
        out = (item in self.category_members)
        return(out)
    def split(self,split_members):
        inclusive = CategoricalSet([i for i in self.category_members if i in split_members])
        exclusive = CategoricalSet([i for i in self.category_members if i not in split_members])
        return(inclusive,exclusive)


class FunctionalSet(Set):
    def __init__(self,membership_function):
        super().__init__()
        self.membership_function = membership_function
    def __contains__(self, item):
        out = self.membership_function(item)
        return(out)
    def split(self,splitting_function):
        inclusive_fn = lambda item, self=self,splitting_function=splitting_function: self.membership_function(item) and splitting_function(item)
        exclusive_fn = lambda item, self=self,splitting_function=splitting_function: self.membership_function(item) and not splitting_function(item)
        inclusive = FunctionalSet(inclusive_fn)
        exclusive = FunctionalSet(exclusive_fn)
        return(inclusive,exclusive)


class OneDimensionalInterval(Set):
    def __init__(self, a, b, left_inclusive, right_inclusive):
        super().__init__()
        self.left_bound = a
        self.right_bound = b
        self.left_inclusive = left_inclusive
        self.right_inclusive = right_inclusive
    def __str__(self):
        out = '[' if self.left_inclusive else '('
        out += str(self.left_bound)
        out += ','
        out += str(self.right_bound)
        out += ']' if self.right_inclusive else ')'
        return(out)
    def __contains__(self, item):
        if self.left_bound < item < self.right_bound:
            return (True)
        if self.left_inclusive and item == self.left_bound:
            return (True)
        if self.right_inclusive and item == self.right_bound:
            return (True)
        return (False)
    def split(self,item,include_in_left):
        left_interval = OneDimensionalInterval(self.left_bound,item,self.left_inclusive,include_in_left)
        right_interval = OneDimensionalInterval(item,self.right_bound,not include_in_left, self.right_inclusive)
        return(left_interval,right_interval)


class MultiDimensionalInterval(Set):
    def __init__(self, a, b, left_inclusive, right_inclusive):
        super().__init__()
        N = len(a)
        if N != len(b) or N != len(left_inclusive) or N != len(right_inclusive):
            raise ValueError('Expected arguments a, b, left_inclusive and right_inclusive to be of same length. Got different lengths.')
        self.dim = N
        self.left_bound = a
        self.right_bound = b
        self.left_inclusive = left_inclusive
        self.right_inclusive = right_inclusive
        self.marginals = [ OneDimensionalInterval(a[idx],b[idx],left_inclusive[idx],right_inclusive[idx]) for idx in range(self.dim) ]
    def __contains__(self, item):
        item = self._check_item_dimension(item)
        out = all( (item[idx] in self.marginals[idx]) for idx in range(self.dim))
        return (out)
    def __str__(self):
        out = 'x'.join([str(marginal) for marginal in self.marginals])
        return(out)
    def split(self,item,include_in_left):
        item = self._check_item_dimension(item)
        include_in_left = self._check_item_dimension(include_in_left)
        out = []
        for sub_box_arguments in itertools.product([ self._make_marginal_left_arguments(item,include_in_left,idx) for idx in range(self.dim) ]):
            out.append(MultiDimensionalInterval(sub_box_arguments))
        out = tuple(out)
        return(out)
    def _make_marginal_left_arguments(self,item,include_in_left,idx):
        left_interval = (
            self.left_bound[idx],
            item[idx],
            self.left_inclusive[idx],
            include_in_left[idx],
        )
        right_interval = (
            item[idx],
            self.right_bound[idx],
            include_in_left[idx],
            self.right_bound[idx],
        )
        return(left_interval,right_interval)
    def _check_item_dimension(self,item):
        if self.dim==1:
            item = [item]
        elif len(item)!=self.dim:
            raise ValueError(f'Expected argument item of length {self.dim}. Got {len(item)} instead.')
        return(item)
