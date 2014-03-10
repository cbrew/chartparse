"""
This is a bottom-up chart parser for a fragment of English.
It uses the active chart datastructure. The design is based
on Steve Isard's LIB CHART, a teaching tool (written in 1983) that
comes with the wonderful Poplog AI development environment
(Details at http://www.poplog.org/gospl/packages/pop11/lib/chart.p
and http://www.poplog.org)

.. moduleauthor: Chris Brew

>>> parse(["the","pigeons",'are','punished','and','they','suffer'])
['the', 'pigeons', 'are', 'punished', 'and', 'they', 'suffer']
Parse 1:
S
 S
  Np
   det the
   Nn
    n pigeons
  cop are
  ppart punished
 conj and
 S
  Np
   pn they
  Vp
   v suffer
1 parses


"""

from english import GRAMMAR, Grammar
from collections import defaultdict
from Queue import PriorityQueue


def _pmul(p1, p2):
    """
    Multiply probabilities.

    
    """
    if p1 and p2:
        return p1 * p2
    else:
        return None


class Edge(object):
    """
    An edge is an assertion about some span of the text. It has a left and
    right boundary, a label, and a sequence of needs. If it has no needs,
    it is said to be B{COMPLETE}, otherwise it is described as B{PARTIAL}

    :type label: string
    :ivar label: the mother node of the constituent.
    :type left: integer(0..n)
    :ivar left: the index of the left boundary of the edge.
    :type right: integer(0..n)
    :ivar right: the index of the right boundary of the edge.
    :type needed: tuple of strings
    :ivar needed: strings representing the categories that the edge needs.
    :type probability: float
    :ivar probability: the inside probability of the edge.

    >>> x = Edge('s',0,1,(), 0.5)

    """
    __slots__ = ('label', 'left', 'right', 'needed', 'probability')



    def __init__(self, label, left, right, needed, probability=None):
        """
        Constructs an edge.

        :type label: string
        :param label: the mother node of the constituent.
        :type left: integer(0..n)
        :param left: the index of the left boundary of the edge.
        :type right: integer(0..n)
        :param right: the index of the right boundary of the edge.
        :type needed: tuple of strings
        :param needed: strings representing the categories that the edge needs.
        """
        self.label = label
        self.left = left
        self.right = right
        self.needed = needed
        self.probability = probability

    def iscomplete(self):
        """
        Test if the edge is complete

        >>> x = Edge('dog',0,1,())
        >>> x.iscomplete()
        True
        >>> x = Edge('s',0,1,('np','vp'))
        >>> x.iscomplete()
        False
        """
        return not self.needed

    def ispartial(self):
        """
        Test if the edge is partial

        >>> x = Edge('dog',0,1,())
        >>> x.ispartial()
        ()
        >>> x = Edge('s',0,1,('np','vp'))
        >>> x.ispartial()
        ('np', 'vp')

        """
        return self.needed

    def __repr__(self):
        """
        This method is part of Python's infrastructure for printing.
        It produces a textual description of the Edge.

        See: http://docs.python.org/\
reference/datamodel.html#object.__repr__
        """
        if self.iscomplete() and isinstance(self.probability, float):
            template = 'C({label},{lhs},{rhs})@{probability:0.4f}'
        elif self.iscomplete() and (self.probability is None):
            template = 'C({label},{lhs},{rhs})'
        elif self.ispartial and isinstance(self.probability, float):
            template = 'P({label},{lhs},{rhs},{needed})@{probability:0.4f}'
        elif self.ispartial and (self.probability is None):
            template = 'P({label},{lhs},{rhs},{needed})'
        else:
            raise ValueError('edge not printable')

        return template.format(
            label=self.label,
            lhs=self.left,
            rhs=self.right,
            needed=self.needed,
            probability=self.probability)

    def __lt__(self, other):
        """
        Rich comparison for edges.

        Assumes that other really is an edge.
        """
        assert isinstance(other, Edge)

        t1 = (self.span_length(),
              self.left,
              self.right,
              self.label,
              self.needed)
        t2 = (other.span_length(),
              other.left,
              other.right,
              other.label,
              other.needed)
        return t1 < t1

    def __gt__(self, other):
        return other < self

    def span_length(self):
        """
        Return the length of a span.
        """
        return self.right - self.left

    def __eq__(self, other):
        """
        This method is required if we want to make Edges usable in
        Python's set and map datastructures.

        @See: U{http://docs.python.org/reference/datamodel.html#object.__eq__}
        """
        return self.label == other.label and self.left == other.left \
            and self.right == other.right and self.needed == other.needed

    def __hash__(self):
        """
        This method is needed in order to ensure that Edges in
        sets and maps are hashable and can compare unequal.

        @See: U{http://docs.python.org/\
reference/datamodel.html#object.__hash__}
        """
        return hash((self.label, self.left, self.right, self.needed))


class Chart(object):

    """An active chart parser.

    @Type partials: list<set<Edge>>
    @Ivar partials: a list of sets Partial edges ending in \
position i are stored in partials[i]
    @Type completes: list<set<Edge>>
    @Ivar completes: a list of sets Complete edges \
starting in position i are stored in completes[i]
    @Type prev: defaultdict<set<Edge>>
    @Ivar prev: mapping from edges to the complete edges that \
gave rise to them: empty for edges not created by fundamental rule
    @Type agenda: deque<Edge>
    @Ivar agenda: The list of edges still remaining to be incorporated.
    """

    def __init__(self, words, grammar=GRAMMAR, verbose=False):
        """
        Create and run the parser

        @Type words: list of string.
        @Param words: the words to be parsed.
        """

        self.verbose = verbose
        self.grammar = grammar.grammar
        self.partials = [set() for _ in range(len(words) + 1)]
        self.completes = [set() for _ in range(len(words) + 1)]
        self.prev = defaultdict(set)
        self.agenda = PriorityQueue()
        for i in range(len(words)):
            self.agenda.put(self.lexical(words[i], i))
        while not self.agenda.empty():
            item = self.agenda.get(block=False)
            if self.verbose:
                print item
            self.incorporate(item)
            self.agenda.task_done()

    def lexical(self, word, i):
        """
        Create a lexical edge based on C{word}

        @Type word: string
        @Param word: the word to base the edge on
        @Type i: integer
        @Param i: where the edge starts
        """
        return Edge(word, i, i + 1, (), probability=1.0)

    def solutions(self, topCat):
        """
        Find the solutions rooted in C{topCat}

        @Type topCat: string
        @Param topCat: the symbol that the sentence should be rooted in.
        @Rtype: list<Edge>
        """
        return [e for e in self.completes[0] if
                e.right == len(self.completes) - 1 and e.label == topCat]

    def add_prev(self, e, c):
        """
        Record information about the B{COMPLETE} predecessor of an edge.
        Taken together with the edge itself, this lets the
        B{PARTIAL} partner be reconstructed.

        @Type e: Edge
        @Param e: an edge that has just been made
        @Type c: Edge
        @Param c: the predecessor of e
        @Rtype: <Edge>
        @Return: the edge whose information has just been recorded.
        """
        self.prev[e].add(c)
        return e

    def get_prev(self, e):
        """
        Return the predcessors of an edge

        @Type e: Edge
        @Param e: the edge whose predecessors are desired
        @Rtype: set<Edge>
        @Return: the predecessors of e
        """
        return self.prev[e]

    def pairwithpartials(self, partials, e):
        """
        Run the fundamental rule for everything in
        partials that goes with e.

        Updates the C{agenda} by adding to its end.

        Probabilities, if present, are propagated.

        :type partials: set<Edge>
        :aram partials: the potential partners of e
        :type e: Edge
        :param e: The complete edge that should be completed
        """
        for p in partials:
            if e.label == p.needed[0]:
                probability = _pmul(e.probability, p.probability)
                self.agenda.put(
                    self.add_prev(Edge(p.label, p.left, e.right,
                                       p.needed[1:],
                                       probability=probability), e))

    def pairwithcompletes(self, e, completes):
        """
        Run the fundamental rule for everything in
        C{completes} that goes with C{e}.

        Updates the C{agenda} by adding to its end.

        :type completes: set<Edge>
        :param completes: the potential partners of e
        :type e: Edge
        :param e: The partial edge that should be completed
        """
        for c in completes:
            if e.needed[0] == c.label:
                probability = _pmul(e.probability, c.probability)
                self.agenda.put(
                    self.add_prev(Edge(e.label, e.left,
                                       c.right, e.needed[1:],
                                       probability=probability), c))

    def spawn(self, lc, i):
        """
        Spawn empty edges from the rules that match C{lc}.
        a spawned edge need only be added the first time that
        it is predicted. Its probability does not depend on how
        many times it is predicted.

        :type lc: string
        :param lc: the label of the left corner item to spawn from.
        :type i: integer
        :param i: the index of the cell where the empty edges are to go.

        >>> ch = Chart([])
        >>> ch.spawn('Np', 0)
        >>> ch.agenda.get(block=False)
        P(S,0,0,('Np', 'Vp'))@0.3901
        """
        for rule in self.grammar:
            lhs = rule.lhs
            rhs = rule.rhs
            if rhs[0] == lc:
                e = Edge(lhs, i, i,
                         tuple(rhs),
                         probability=rule.probability
                         )
                if e not in self.partials[e.left]:
                    self.agenda.put(e)

    def incorporate(self, e):
        """
        Add C{e} to the chart and trigger all corresponding actions.

        @Type e: Edge
        @Param e: the edge to be added
        """
        if e.iscomplete():
            if e in self.completes[e.left]:
                for prev in self.completes[e.left]:
                    if prev == e:
                        prev.probability += e.probability
            else:
                self.completes[e.left].add(e)
                self.spawn(e.label, e.left)
                self.pairwithpartials(self.partials[e.left], e)
        elif e.ispartial():
            if e in self.partials[e.right]:
                for prev in self.partials[e.right]:
                    if prev == e:
                        prev.probability += e.probability
            else:
                self.partials[e.right].add(e)
                self.pairwithcompletes(e, self.completes[e.right])
        else:
            raise "Huh? edge has to be either partial or complete!"

    def trees(self, e):
        """
        Generate the trees that are rooted in edge.

        @Type e: Edge
        @Param e: the chart entry whose daughters we trace
        @See: U{http://www.ibm.com/developerworks/library/l-pycon.html}
        for a good explanation of Python generators,
        which are used here.
        """
        prev = self.get_prev(e)
        if prev:
            for c in prev:
                for p in self.partials[c.left]:
                    if p.needed[0] == c.label and p.label == e.label and\
                            p.left == e.left and p.needed[1:] == e.needed:
                        for left in self.trees(p):
                            for right in self.trees(c):
                                yield Tree(e.label,
                                           left.children + tuple([right]),
                                           probability=e.probability)
        else:
            yield Tree(e.label, probability=e.probability)


class Tree(object):

    """
    Container for syntax trees.

    @Type parent: string
    @Ivar parent: label of parent node
    @Type children: tuple<Tree>
    @Ivar children: the subtrees (possibly empty).
    """

    def __init__(self, parent, children=(), probability=None):
        self.parent = parent
        self.children = children
    __slots__ = ["parent", "children", "probability"]


def treestring(t, tab=0):
    """
    Return a string representation of a syntax tree.
     - Print preterminals on same line as their terminals
       (e.g. n dog)
     - Use indentation to signal level

     >>> print treestring(Tree("S",[Tree("NP"),Tree("VP")]))
     S
      NP
      VP
     <BLANKLINE>


    @Type t: syntax tree
    @Param t: representation of a tree to be printed
    """

    if len(t.children) == 1 and t.children[0].children == ():
        s = (' ' * tab) + t.parent + ' ' + t.children[0].parent + '\n'
    else:
        s = (' ' * tab) + t.parent + '\n'
        for child in t.children:
            s += treestring(child, tab + 1)
    return s


def parse(sentence, verbose=False):
    """
    Print out the parses of a sentence


    @Type sentence: list<string>
    @Param sentence: the words to be parsed


    >>> parse(["the","pigeons",'are','punished','and','they','suffer'])
    ['the', 'pigeons', 'are', 'punished', 'and', 'they', 'suffer']
    Parse 1:
    S
     S
      Np
       det the
       Nn
        n pigeons
      cop are
      ppart punished
     conj and
     S
      Np
       pn they
      Vp
       v suffer
    1 parses

    """
    v = Chart(sentence, verbose=verbose)
    print sentence
    i = 0
    for e in v.solutions('S'):
        for tree in v.trees(e):
            i += 1
            print "Parse %d:" % i
            print treestring(tree),
    print i, "parses"


def aas_grammar():
    """
    >>> aas_grammar()
    """

    v = Chart(["a", "a", "a"], grammar=Grammar(
        """S -> S S
S -> w""", "a w"))

    print v.completes
    """
    i = 0
    for e in v.solutions('S'):
        for tree in v.trees(e):
            i += 1
            print "Parse %d:" % i
            print treestring(tree),
    print i, "parses"
    """
