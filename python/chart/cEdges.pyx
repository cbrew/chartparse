# cython: profile=True

from collections import namedtuple
import re


COMPLEX_CATEGORY=re.compile(r"(\w*)\s*\(([^)]+)\)")

def restring(x):
        return "\n".join(map(str,x))


class ImmutableCategory(namedtuple("ImmutableCategory",("cat","features"))):
    """
    A syntactic category, with atomic features.
    """
    def __repr__(self):
        if not self.features:
            return "{cat}".format(cat=self.cat)
        else:
            return "{cat}({fs})".format(cat=self.cat,fs=",".join([":".join(x) for x in sorted(self.features)]))

    def getfeat(self, key, default=None):
        """
        Obtain the value of a feature.

        >>> c = ImmutableCategory.from_string('Np(case:subj,num)')
        >>> c.getfeat('case')
        'subj'
        """
        try:
            return dict(self.features)[key]
        except:
            return default

    def extend(self, key, value):
        """
        Add a feature with given value.
        Return a copy, because categories are immutable.

        >>> c = ImmutableCategory.from_string('Np(case:subj,num)')
        >>> c.extend('anim','animate')
        Np(anim:animate,case:subj)

        >>> c = ImmutableCategory.from_string('Np(case:subj,num)')
        >>> c.extend('case','obj')
        Np(case:obj)

        """
        d = dict(self.features)
        d[key]=value
        return ImmutableCategory(self.cat,frozenset([tuple(x) for x in d.items()]))

    def extendc(self, constrain_keys, category):
        c = self
        for k in constrain_keys:
            v = category.getfeat(k, None)
            if v:
                c = c.extend(k,v)
        return c

    def leq_general(self,c):
        return self == c or self.less_general(c)

    def less_general(self,c):
        """
        Check subsumption relation between self
        and c. True if self is strictly more
        specific than c.

        >>> c1 = ImmutableCategory.from_string('A')
        >>> c2 = ImmutableCategory.from_string('A(num:sing)')
        >>> c3 = ImmutableCategory.from_string('A(case:subj)')
        >>> c4 = ImmutableCategory.from_string('B')
        >>> c5 = ImmutableCategory.from_string('A(num:sing,case:obj)')
        >>> c6 = ImmutableCategory.from_string('A(num:sing,case:subj)')
        >>> c1.less_general(c2)
        False
        >>> c2.less_general(c1)
        True
        >>> c3.less_general(c1)
        True
        >>> c1.less_general(c4)
        False
        >>> c4.less_general(c1)
        False
        >>> c3.less_general(c5)
        False
        >>> c5.less_general(c3)  
        False
        >>> c6.less_general(c3)
        True
        >>> c3.less_general(c6)
        False
        >>> c1.less_general(c1)
        False
        >>> c2.less_general(c2)
        False



        """
        if self.cat != c.cat:
            return False

        elif self.features is None:
            # there are no features on self, so
            # it cannot be more specific.
            return False
        elif c.features is None:
            # there are features on self but not on c
            # therefore self is more specific
            return True
        else: 
            # 
            return self.features > c.features



    @staticmethod
    def from_string(xx):

        """

        >>> c = ImmutableCategory.from_string('Np(case:subj,num)')
        >>> c
        Np(case:subj)
        """
        if '(' in xx:
            m = COMPLEX_CATEGORY.match(xx)
            assert m,xx
            cat,fs=m.groups()
            return ImmutableCategory(cat=cat, features=ImmutableCategory._feats(fs.split(',')))

        else:
            return ImmutableCategory(cat=xx,features=frozenset())


    @staticmethod
    def constraints(xx):
        """
        Extract the constraints mentioned on the spec. These are
        meaningful only in the context of a rule, so do not form
        part of the category itself.

        >>> ImmutableCategory.constraints('Np(case:subj,num)')
        frozenset(['num'])

        >>> ImmutableCategory.constraints('Np(case,tr,num)')
        frozenset(['case', 'num', 'tr'])

        """
        if '(' in xx:
            m = COMPLEX_CATEGORY.match(xx)
            assert m,xx
            cat,fs=m.groups()
            return frozenset([f.strip() for f in fs.split(',') if ':' not in f])
        else:
            return frozenset()


    @staticmethod
    def _feats(fs):
        return frozenset([tuple(f.split(':')) for f in fs if ':' in f])

    def fcheck(c1,c2):
        """
        Check for a clash between features. N.B. this code
        is in the inner loop, and may need speeding up.

        >>> c1 = ImmutableCategory.from_string('A')
        >>> c2 = ImmutableCategory.from_string('A(num:sing)')
        >>> c3 = ImmutableCategory.from_string('A(num:pl)')
        >>> c4 = ImmutableCategory.from_string('A(num:sing,case:obj)')
        >>> c5 = ImmutableCategory.from_string('A(num:sing,case:subj)')
        >>> c6 = ImmutableCategory.from_string('B')
        >>> c1.fcheck(c2)
        True
        >>> c2.fcheck(c1)
        True
        >>> c1.fcheck(c3)
        True
        >>> c2.fcheck(c3)
        False
        >>> c3.fcheck(c2)
        False
        >>> c4.fcheck(c5)
        False
        >>> c5.fcheck(c4)
        False

        """


        ff1 = c1.features
        ff2 = c2.features

        unshared = ff1 ^ ff2

        # if the keys are all disjoint,
        # unshared will be the same length
        # as the dict built on it. Otherwise
        # unshared will be longer.
        return len(dict(unshared)) == len(unshared)


icat = ImmutableCategory


class Edge(namedtuple("Edge", ('label', 'left', 'right', 'needed','constraints'))):
    """An edge is an assertion about some span of the text. It has a left and
    right boundary, a label, and a sequence of needs. If it has no needs,
    it is said to be **complete**, otherwise it is described as **partial**.

    This code needs some work to make sense when the category is complex.


    Attributes
    ----------
    label : string
        the mother node of the constituent.
    left: integer [0..n]
        the index of the left boundary of the edge.
    right: integer[0..n]
        the index of the right boundary of the edge.
    needed: strings
        strings representing the categories that the edge needs.
    constraints: set(string)
        features inherited from the spawning rule.

    Parameters
    ----------
    label : string
        the mother node of the constituent.
    left: integer [0..n]
        the index of the left boundary of the edge.
    right: integer[0..n]
        the index of the right boundary of the edge.
    needed: strings
        strings representing the categories that the edge needs.
    

    Examples
    --------

    >>> Edge('s',0,1,(),None)
    C(s, 0, 1)
    
    """
    def __new__(cls, label, left, right, needed, constraints):
        if constraints is None: 
            constraints = (frozenset(),tuple([frozenset() for _ in needed]))
        return super(Edge, cls).__new__(cls,label=label,left=left,right=right,needed=needed,constraints=constraints)

    def less_general(self,e):

        """
        Check edges for strict differences in generality. 

        >>> e1 = Edge(label=icat.from_string('S(num:pl)'),left=0,right=2,needed=tuple([icat.from_string('Vp')]),constraints=None)
        >>> e2 = Edge(label=icat.from_string('S(num:pl)'),left=0,right=2,needed=tuple([icat.from_string('Vp')]),constraints=None)
        >>> e3 = Edge(label=icat.from_string('S'),left=0,right=2,needed=tuple([icat.from_string('Vp')]),constraints=None)
        >>> e4 = Edge(label=icat.from_string('S(num:pl,case:obj)'),left=0,right=2,needed=tuple([icat.from_string('Vp')]),constraints=None)
        >>> e5 = Edge(label=icat.from_string('S(num:pl)'),left=0,right=2,needed=tuple([icat.from_string('Vp(case:obj)')]),constraints=None)
        >>> e1.less_general(e1)
        False
        >>> e1.less_general(e2)
        False
        >>> e2.less_general(e1)
        False
        >>> e1.less_general(e3)
        True
        >>> e3.less_general(e1)
        False
        >>> e1.less_general(e4)
        False
        >>> e4.less_general(e1)
        True
        >>> e5.less_general(e1)
        True
        >>> e1.less_general(e5)
        False
        """
        return (not isinstance(e.label, str) and 
                (e.left == self.left) and (e.right == self.right) and
                (self.label != e.label or self.needed != e.needed) and 
                self.label.leq_general(e.label) and 
                len(self.needed) == len(e.needed) and
                self.constraints_leq_general(e) and 
                all([e1.leq_general(e2) for e1,e2 in zip(self.needed,e.needed)]))
        
    def constraints_leq_general(self,e):
        """
        Check constraints. True if self's constraints are
        more specific.

        XXX Currently not operational.

        """
        return True

        

    def iscomplete(self):
        """
        Test if the edge is complete.

        Examples
        --------

        >>> x = Edge('dog',0,1,(),None)
        >>> x.iscomplete()
        True
        >>> x = Edge('s',0,1,('np','vp'),None)
        >>> x.iscomplete()
        False
        """
        return not self.needed

    def ispartial(self):
        """
        Test if the edge is partial.

        Examples
        --------

        >>> x = Edge('dog',0,1,(),None)
        >>> x.ispartial()
        ()
        >>> x = Edge('s',0,1,('np','vp'),None)
        >>> x.ispartial()
        ('np', 'vp')

        """
        return self.needed

    def percolate(self, cat):
        """
        This is called when an edge has been
        created by consuming the specified
        category. This may result in percolation
        of features to the parent and remaining
        siblings.

        It produces a new edge, in which the
        atomic features on cat are copied onto
        the original symbols.

        """

        # non-op if working with comple categories
        if isinstance(self.label,str):
            return self

        #     
        cs = self.constraints
        newlabel = self.label.extendc(cs[0], cat)
        # N.B. this is where we cut away the first item in the constraints field.
        newneeded = tuple([r.extendc(c, cat) for c,r in zip(cs[1][1:],self.needed)])
        return Edge(label = newlabel,
                   left=self.left,
                    right=self.right,
                    needed=newneeded,
                    constraints= (cs[0],cs[1][1:]))
        
        return self


    def __repr__(self):
        """
        Produces a textual description of the Edge.

        Part of Python's infrastructure for printing.

        See Also
        --------
    
        http://docs.python.org/reference/datamodel.html#object.__repr__

        Examples
        --------
        >>> Edge('dog',0,1,(),None)
        C(dog, 0, 1)
        """
    
        if self.iscomplete():
            template = 'C({label}, {lhs}, {rhs})'
        elif self.ispartial:
            template = 'P({label}, {lhs}, {rhs},{needed})'
        else:
            raise ValueError('edge not printable')

        return template.format(
            label=self.label,
            lhs=self.left,
            rhs=self.right,
            needed=self.needed)

    def __lt__(self, other):
        """Rich comparison for edges.

        XXX inner loop.
        """
        cdef int s1
        cdef int s2


        s1 = self.right - self.left
        s2 = other.right - other.left
        if s1 < s2:
            return True
        elif s2 < s1:
            return False

        l1 = self.label
        l2 = other.label
         
        if l1 < l2:
            return True
        elif l2 < l1:
            return False
        
        return self.needed < other.needed

    def __gt__(self, other):
        """Rich comparison for edges.
        """
        return other < self #pragma no cover

    def span_length(self):
        """
        Return the length of a span, in words.
        """


        return self.right - self.left

    def __eq__(self, other):
        """
        This method is required because we want to make Edges usable in
        Python's set and map datastructures.

        See Also
        --------
        http://docs.python.org/reference/datamodel.html#object.__eq__

        """
        return self.label == other.label and self.left == other.left \
            and self.right == other.right and self.needed == other.needed

    def __hash__(self):
        """
        This method is needed in order to ensure that Edges in
        sets and maps are hashable and can compare unequal.

        See Also
        --------
        http://docs.python.org/reference/datamodel.html#object.__hash__

        """
        return hash((self.label, self.left, self.right, self.needed))