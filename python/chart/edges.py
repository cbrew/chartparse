# -*- coding: utf-8 -*-
from collections import namedtuple
from features import ImmutableCategory as icat

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
        Check edges for strict differences in generality. Expected to be called only when features are being used.

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
        return ((e.left == self.left) and (e.right == self.right) and
                (self.label != e.label or self.needed != e.needed) and 
                self.label.leq_general(e.label) and 
                len(self.needed) == len(e.needed) and
                all([e1.leq_general(e2) for e1,e2 in zip(self.needed,e.needed)]))
        
 

        

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

        Is called only when features are being used.
        """
     
        cs = self.constraints
        newlabel = self.label.extendc(cs[0], cat)
        # N.B. this is where we cut away the first item in the constraints field.
        newneeded = tuple([r.extendc(c, cat) for c,r in zip(cs[1][1:],self.needed)])
        return Edge(label = newlabel,
                    left=self.left,
                    right=self.right,
                    needed=newneeded,
                    constraints= (cs[0],cs[1][1:]))

    
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
        
        # pragma: no cover
        if self.iscomplete():
            template = 'C({label}, {lhs}, {rhs})'
        else: 
            assert self.ispartial
            template = 'P({label}, {lhs}, {rhs},{needed})'


        return template.format(
            label=self.label,
            lhs=self.left,
            rhs=self.right,
            needed=self.needed)

    def __lt__(self, other):
        """Rich comparison for edges.

        XXX inner loop. Called from hpush...
        """

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



# The idea from Stabler's "Top down recognizers for MGs and MCFGs" calls for the recognition sequence to be represented by
# a pair of the remaining input string and a priority queue of `indexed atoms`.  In a chart parsing setting, the remaining
# input string is encoded by the end position of the edge, so the only thing that is needed is the priority queue.
#
# The grammar in that paper recognizes a^{i}b^{j}c^{i}d^{j} i,j > 0
# 
# S(x0x1x2x3) -> AC(x0,x2)BD(x1,x3)
# AC(x0x2,x1x3) -> A(x0)C(x1)AC(x2,x3)
# AC(x0,x1) ->  A(x0)C(x1)
# BD(x0x2,x1x3) -> B(x0)D(x1)BD(x2,x3)
# BD(x0,x1) ->  B(x0)D(x1)
# A(a)
# B(b)
# C(c)
# D(d)
# 
# A variable free form of that grammar is that used by Peter Ljunglöf, which is shown below. The fourth
# field of each rule describes the function that maps the yields of the daughters into the yield of the
# result.

stab_abcd = [('s', 'S', ['AC','BD'],[[(0,0),(1,0),(0,1),(1,1)]]),   # Stabler notates this as AC(0,2)BC(1,3), which implicitly says that S is 0123 
             ('ac+','AC',['AC'],[['a',(0,0)],['c',(0,1)]]),
             ('ac','AC',[],[['a'],['c']]),
             ('bd+','BD',['BD'],[['b',(0,0)],['d',(0,1)]]),         # putting 'b','d' in signals leaves
             ('bd','BD',[],[['b'],['d']]),                          # no subconstituents, but does have leaves
             ]










