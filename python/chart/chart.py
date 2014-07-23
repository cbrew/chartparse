"""
This is a bottom-up chart parser for a fragment of English.

It uses the active chart datastructure. The design is based
on Steve Isard's LIB CHART, a teaching tool (written in 1983) that
comes with the wonderful Poplog AI development environment.

This has been adjusted to work with a lattice of input possibilities.


References
----------

The original LIB CHART [1]_ and the Poplog website [2]_

.. [1] http://www.poplog.org/gospl/packages/pop11/lib/chart.p

.. [2] http://www.poplog.org

Examples
--------

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

##
# Created 10 March 2014
# author: Chris Brew
# author: Stephen Isard
# license: Apache 2.0
##


from collections import defaultdict, namedtuple
from heapq import heappush as hpush
from heapq import heappop as hpop

from english import GRAMMAR
import features
import english
from features import ImmutableCategory as icat




class LinearWords(object):
    """
    A class that implements the finite state machine abstraction 
    for the easy case of a linear sequence of words.

    This is the protocol that the any finite state machine must
    implement for input. It must have a final state, with a number ``n``,
    and previous states from 0 to n-1.

    """
    def __init__(self, words):
        self.words = words

    @property
    def final_state(self):
        return len(self.words)

    def arcs(self):
        """
        Enumerate the arcs of simple linear finite-state machine.
        """
        for i,w in enumerate(self.words):
            yield i,w , i+1


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

        if self.constraints and cat.features:
            lhsc = self.constraints[0]
            rhsc = self.constraints[1]
            d = dict(cat.features)
            keys = lhsc.union(*rhsc)

            

            
             


        
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
        return t1 < t2

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

   



class Chart(object):

    """An active chart parser.

    Parameters
    ----------
    words: list of string.
        the words to be parsed.
    grammar: Grammar
        the grammar to parse against.
    verbose: boolean
        provide more logging if true.

    Attributes
    ----------

    partials: list<set<Edge>>
        a list of sets of partial edges ending in 
        position i are stored in partials[i]
    completes: list<set<Edge>>
        a list of sets of complete edges 
        starting in position i are stored in completes[i]
    prev: defaultdict of set of Edge
        mapping from edges to the complete edges that 
        gave rise to them: empty for edges not created by fundamental rule
    agenda: priority queue of edges
        The list of edges still remaining to be incorporated.

    """

    def __init__(self, words, grammar=GRAMMAR, verbose=False, input_source=LinearWords, run=True, using_features=False):
        """
        Create and run the parser.
        """
        self.using_features = using_features    
        self.input_source = input_source
        self.verbose = verbose
        self.grammar = grammar.grammar
        self.prev = defaultdict(set)
        self.agenda = []
        self.seed_agenda(words)
        
        if run:
            while self.agenda:
                item = hpop(self.agenda)
                if self.verbose:
                    print item   #pragma no cover
                self.incorporate(item)

    def show(self):
        print self.partials
        print self.completes

    def setup_words(self, words):
        """
        Instantiate the source of words.
        """
        if self.using_features:
            words = [icat.from_string(w) for w in words]


        return self.input_source(words)
    
    def seed_agenda(self, words):
        """
        Go through the words, seeding the agenda.

        Uses an interface where the
        object that introduces the words is a finite-state
        machine whose arcs can be enumerated.
        """
        words = self.setup_words(words)
        final_state = words.final_state

        self.partials = [set() for _ in range(final_state + 1)]
        self.completes = [set() for _ in range(final_state + 1)]

        for i,w,j in words.arcs():
             hpush(self.agenda,self.lexical(i,w,j))

    def lexical(self, i, word, j):
        """
        Create a lexical edge based on `word`.

        Parameters
        ----------
        word: string
            the word to base the edge on,
        i: integer
            where the edge starts
        j: integer
            where the edge ends

        """
        return Edge(label=word, left=i, right=j, needed=(),constraints=None)

    def solutions(self, topCat):
        """
        Find the solutions rooted in `topCat`

        Parameters
        ----------
        topCat: string
            the symbol that the sentence should be rooted in.
        
        Returns
        -------
        solutions:list<Edge>
        
        """
        return [e for e in self.completes[0] if
                e.right == len(self.completes) - 1 and self.compatible(topCat,e.label)]

    def add_prev(self, e, c):
        """
        Record information about a **complete** predecessor of an edge.
        
        Taken together with the edge itself, this lets the
        **partial** partner be reconstructed.

        Parameters
        ----------
        e: Edge
            an edge that has just been made.
        c: Edge
            a predecessor of `e`, not necessarily the only one.

        Returns
        -------
            e: Edge
                the edge whose information has just been recorded.

        """
        self.prev[e].add(c)
        return e

    def get_prev(self, e):
        """
        Return the predecessors of an edge.

        Parameters
        ----------
        e: Edge
            the edge whose predecessors are desired.
        
        Returns
        -------
        edges : set [Edge] 
            the predecessors of `e`

        """
        return self.prev[e]

    def pairwithpartials(self, partials, e):
        """
        Run the fundamental rule for everything in
        `partials` that goes with `e`.

        Updates the `agenda` by adding to its end.

        Probabilities, if present, are propagated.

        Parameters
        ----------
        partials: set<Edge>
            the potential partners of `e`
        e: Edge
            The complete edge that should be augmented.

        """
        for p in partials:
            if self.compatible(e.label,p.needed[0]):
                hpush(self.agenda,
                       self.add_prev(Edge(label=p.label, 
                                        left=p.left, 
                                        right=e.right,
                                        needed=p.needed[1:],
                                        constraints=p.constraints).percolate(e.label), e))

    def pairwithcompletes(self, e, completes):
        """
        Run the fundamental rule for everything in
        `completes` that goes with `e`.

         Updates the `agenda` by adding to its end.

        Probabilities, if present, are propagated.


        Updates the `agenda`.

        :type completes: set<Edge>
        :param completes: the potential partners of e
        :type e: Edge
        :param e: The partial edge that should be completed.

        """
        for c in completes:
            if self.compatible(e.needed[0],c.label):
                hpush(self.agenda,
                    self.add_prev(Edge(label=e.label, left=e.left,
                                       right=c.right, 
                                       needed=e.needed[1:],
                                       constraints=e.constraints).percolate(c.label), c))

    def compatible(self,rule_category, chart_category):
        """

        """
        if isinstance(rule_category, str) and isinstance(chart_category, str):
            return rule_category == chart_category
        elif isinstance(rule_category, icat) and isinstance(chart_category,icat):
            if rule_category.cat != chart_category.cat:
                return False

            # check the features, Fail if atomic features conflict

            if not icat.fcheck(rule_category, chart_category):
                return False

            # otherwise True
            return True
        else:
            raise ValueError((rule_category, chart_category))

    def spawn(self, lc, i):
        """
        Spawn empty edges at `i` from the rules that match `lc`.

        a spawned edge need only be added the first time that
        it is predicted. 


        Updates the `agenda`.


        Parameters
        ----------
        lc: string or Category
            the label of the left corner item to spawn from.
        i: integer
            the index of the cell where the empty edges are to go.

        Examples
        --------
        >>> ch = Chart([])
        >>> ch.spawn('Np', 0)
        >>> ch.agenda[0]
        P(Np, 0, 0,('Np', 'Pp'))


        """
        for rule in self.grammar:
            lhs = rule.lhs
            rhs = rule.rhs
            if self.compatible(rhs[0], lc):
                e = Edge(label=lhs, left=i, right=i,
                         needed=tuple(rhs),
                         constraints=rule.constraints
                         )
                if e not in self.partials[e.left]:
                    hpush(self.agenda,e)

    def incorporate(self, e):
        """
        Add e to the chart and trigger all corresponding actions.

        Parameters
        ----------
        e: Edge
         the edge to be added.

        Examples
        --------

        >>> ch = Chart(['the'])
        >>> ch.incorporate(Edge('s',0,0,('banana',),None))
        >>> ch.incorporate(Edge('s',0,0,('banana',),None))
        >>> sorted(ch.partials[0])[-1:]
        [P(s, 0, 0,('banana',))]

        >>> ch = Chart([])
        >>> ch.incorporate(Edge('np',0,1,(),None))
        >>> ch.incorporate(Edge('np',0,1,(),None))
        >>> ch.completes[0]
        set([C(np, 0, 1)])

        """
        if e.iscomplete():
            if e in self.completes[e.left]:
                pass
            else:
                self.completes[e.left].add(e)
                # TODO the empty edge produced by spawn
                # will immedidately combine with e
                # so we could make the result directly.
                self.spawn(e.label, e.left)
                self.pairwithpartials(self.partials[e.left], e)
        elif e.ispartial():
            if e in self.partials[e.right]:
                pass
            else:
                self.partials[e.right].add(e)
                self.pairwithcompletes(e, self.completes[e.right])
        else:
            raise "Huh? edge has to be either partial or complete!"  #pragma no cover

    def trees(self, e):
        """
        Generate the trees that are rooted in edge.

        Parameters
        ==========

        e: Edge
            the chart entry whose daughters we trace.

        
        """
        prev = self.get_prev(e)
        if prev:
            for c in prev:
                for p in self.partials[c.left]:
                    if self.compatible(p.needed[0], c.label) and self.compatible(p.label,e.label) and\
                            p.left == e.left and p.needed[1:] == e.needed:
                        for left in self.trees(p):
                            for right in self.trees(c):
                                yield Tree(e.label,
                                           left.children + tuple([right]))
        else:
            yield Tree(e.label)






class Tree(object):

    """
    Container for syntax trees.

    Attributes
    ----------
    parent: string
        label of parent node.
    children: tuple<Tree>
        the subtrees (possibly empty).
    """
    ["parent", "children"]
    
    def __init__(self, parent, children=()):
        self.parent = parent
        self.children = children
    


def treestring(t, tab=0,sep=' '):
    """

    Return a string representation of a syntax tree.
    
    Print preterminals on same line as their terminals
       
       (e.g. n dog)

    Use indentation to signal nesting level.

     Parameters
    ==========
    t: syntax tree
        The tree to be printed.

     Examples
     ========

     >>> print treestring(Tree("S",[Tree("NP"),Tree("VP")]))
     S
      NP
      VP
     <BLANKLINE>


    >>> print treestring(Tree("S",[Tree("NP"),Tree("VP")]),sep='_')
    S
    _NP
    _VP
    <BLANKLINE>

   
    """

    if len(t.children) == 1 and t.children[0].children == ():
        s = (sep * tab) + str(t.parent) + ' ' + str(t.children[0].parent) + '\n'
    else:
        s = (sep * tab) + str(t.parent) + '\n'
        for child in t.children:
            s += treestring(child, tab=tab + 1,sep=sep)
    return s


def parse(sentence, verbose=False, topcat='S', grammar=GRAMMAR,sep=' ', input_source=LinearWords, use_features=False,show_chart=False):
    """
    Print out the parses of a sentence


    Parameters
    ----------

    sentence: list<string>
        the words to be parsed.

    Examples
    --------

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

     >>> parse(["the","pigeons",'are','punished','and','they','blink'])
     ['the', 'pigeons', 'are', 'punished', 'and', 'they', 'blink']
     No parse

    """
    if use_features:
        grammar = features.Grammar(list(features.compile_grammar(english.RULES)) + list(features.compile_lexicon(english.WORDS)))
        topcat = icat.from_string(topcat)


    v = Chart(sentence, verbose=verbose,grammar=grammar,input_source=input_source, using_features=use_features)

    if show_chart:
        v.show()
        print v.solutions(topcat)

    print sentence
    i = 0
    sols = v.solutions(topcat)
    if len(sols) == 0:
        print "No parse"
    else:
        for e in sols:
            for tree in v.trees(e):
                i += 1
                print "Parse %d:" % i
                print treestring(tree, tab=0, sep=sep),
        print i, "parses"


