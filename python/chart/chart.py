"""
This is a bottom-up chart parser for a fragment of English.

It uses the active chart datastructure. The design is based
on Steve Isard's LIB CHART, a teaching tool (written in 1983) that
comes with the wonderful Poplog AI development environment.

This has been adjusted to work with a lattice of input possibilities,
and to have a simple feature system.


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

>>> parse(["the","pigeons",'are','punished','and','they','suffer',"and","they","suffer"])
['the', 'pigeons', 'are', 'punished', 'and', 'they', 'suffer', 'and', 'they', 'suffer']
Parse 1:
S
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
 conj and
 S
  Np
   pn they
  Vp
   v suffer
Parse 2:
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
  S
   Np
    pn they
   Vp
    v suffer
  conj and
  S
   Np
    pn they
   Vp
    v suffer
2 parses

"""

##
# Created 10 March 2014
# author: Chris Brew
# author: Stephen Isard
# license: Apache 2.0
##


from collections import defaultdict, namedtuple
from english import GRAMMAR
import features
import english
from features import ImmutableCategory as icat
import operator


def hpush(heap,item):
    """
    Simple list based alternative to heapq.heappop()
    Reduces need for comparisons in agenda. Much
    faster, and all current tests pass.
    """
    heap.append(item)

def hpop(heap):
    """
    Simple list based alternative to heapq.heappop().
    Reduces need for comparisons in agenda. Much
    faster, and all current tests pass.
    """
    return heap.pop()


# from heapq import heappop as hpop
# from heapq import heappush as hpush


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

from edges import Edge


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
    using_features: boolean
        use categories with features on them if true.

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
        self.countdict = defaultdict(int)
        self.agenda = []
        self.seed_agenda(words)
        if self.using_features:
            self.compat = self.compatible
        else:
            self.compat = operator.eq
        
        if run:
            while self.agenda:
                item = hpop(self.agenda)
                if self.verbose:
                    print item   #pragma no cover
                self.incorporate(item)

    def show(self):
        for p in self.partials:
            for e in p:
                print e
        for c in self.completes:
            for e in c:
                print e
                    

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

        

        self.partials =  [set() for _ in range(final_state + 1)]
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

    def solutions(self, topCat,n=None):
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
        r = [e for e in self.completes[0] if
                e.right == len(self.completes) - 1 and self.compat(topCat,e.label)]
        if n is not None:
            return r[n]
        else:
            return r

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


        Parameters
        ----------
        partials: set<Edge>
            the potential partners of `e`
        e: Edge
            The complete edge that should be augmented.

        """
        for p in partials:
            if self.compat(e.label,p.needed[0]):
                newedge = Edge(label=p.label, 
                                        left=p.left, 
                                        right=e.right,
                                        needed=p.needed[1:],
                                        constraints=p.constraints)
                if self.using_features:
                    newedge = newedge.percolate(e.label)
                hpush(self.agenda,
                       self.add_prev(newedge, e))

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
            if self.compat(e.needed[0],c.label):
                newedge = Edge(label=e.label, left=e.left,
                                       right=c.right, 
                                       needed=e.needed[1:],
                                       constraints=e.constraints)
                if self.using_features:
                    newedge = newedge.percolate(c.label)
                hpush(self.agenda,self.add_prev(newedge, c))

    def compatible(self,rule_category, chart_category):
        """
        Compatibility check.  Called only when features are being used.
        """
        return (rule_category.cat == chart_category.cat)  and rule_category.fcheck(chart_category)
        
    

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
        >>> sorted(ch.agenda)[0]
        P(Np, 0, 0,('Np', 'Pp'))


        """
        for rule in self.grammar:
            lhs = rule.lhs
            rhs = rule.rhs
            if self.compat(rhs[0], lc):
                e = Edge(label=lhs, left=i, right=i,
                         needed=tuple(rhs),
                         constraints=rule.constraints
                         )
                if e not in self.somepartials(right=e.left):
                    self.prev[e] = set()
                    hpush(self.agenda,e)

    def find(self,e):
        if e.iscomplete():
            edges = self.completes[e.left]
        else:
            edges = self.partials[e.right]

        # there will be zero or one edge in the chart that satisfies
        # the criteria...
        for edge in edges:
            if edge.left == e.left and edge.right == e.right  and self.compat(edge.label,e.label) and self.allcompatible(edge.needed, e.needed):
                    return edge


    def membership_check(self, e, previous):
        """
        Check whether edge or equivalent
        is present. 

        Four cases

        1) edge is present, return True and original set.
        2) edge is entirely absent: return False and original set.
        3) edge is less general than one in the set, return True and original set
        4) edge is more general than one in the set, return True and modified set
           that replaces the more specific with the new edge.

        """
        if e in previous:
            return True,previous

        if not self.using_features:
            return False,previous



        for p in previous:
            if e.less_general(p):
                return True,previous
            elif p.less_general(e):
                return True, (previous - set([p])) | set([e]) 
        return False,previous

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
            flag,self.completes[e.left] = self.membership_check(e, self.completes[e.left])
            if flag:  # no new edge needs to be added
                pass
            else:
                self.completes[e.left].add(e)
                # TODO the empty edge produced by spawn
                # will immedidately combine with e
                # so we could make the result directly.
                self.spawn(e.label, e.left)
                self.pairwithpartials(self.somepartials(right=e.left), e)
        elif e.ispartial():

            flag,self.partials[e.right] = self.membership_check(e, self.partials[e.right])
            if flag: # no new edge needs to be added
                pass
            else:
                self.partials[e.right].add(e)
                self.pairwithcompletes(e, self.completes[e.right])
        else:
            raise "Huh? edge has to be either partial or complete!"  #pragma no cover

    def allcompatible(self,cs1,cs2):
        if len(cs1) != len(cs2):
            return False
        for c1,c2 in zip(cs1,cs2):
            if not self.compat(c1,c2):
                return False
        return True

    def trace_edges(self,sol=None):
        """
        Recursive procedure to find counts
        of edges.

        >>> v = parse(('the pigeons are punished' + ( ' and they suffer' * 4)).split(),return_chart=True, print_trees=False)
        >>> v.trace_edges()
        14
        >>> v = parse(('the pigeons are punished' + ( ' and they suffer' * 5)).split(),return_chart=True, print_trees=False)
        >>> v.trace_edges()
        42
        """
        if sol is None:
            self._traced = dict()
            s = 0
            for sol in self.solutions(self.topcat):
                self.trace_edges(sol=sol)
                s += self._traced[sol]
            return s
        elif sol in self._traced:
            pass
        else:
            ps = self.prev[sol]
            if ps:
                self._traced[sol] = 0
                for e in self.prev[sol]:
                    probe = Edge(label=sol.label,
                                left=sol.left,
                                right=e.left,
                                needed = (e.label,) + sol.needed,
                                constraints=sol.constraints)
                    probe = self.find(probe)
                    self.trace_edges(probe)
                    self.trace_edges(sol=e)
                    self._traced[sol] += self._traced[e]*self._traced[probe]
            else:
                self._traced[sol] = 1



    def count(self,e):
        """
        Count the trees that are rooted in edge.

        Parameters
        ==========

        e: Edge
            the chart entry whose analyses we count.

        Tests
        =====

        Check that counting of ambiguous parses works as advertised. Numbers are, as theory dictates
        from the Catalan series, which grows very fast.

        >>> v = parse(('the pigeons are punished' + ( ' and they suffer' * 0)).split(), use_features=True, print_trees=False, return_chart=True)
        >>> v.count(v.solutions(v.topcat,0))
        1

        >>> v = parse(('the pigeons are punished' + ( ' and they suffer' * 1)).split(), use_features=True, print_trees=False, return_chart=True)
        >>> v.count(v.solutions(v.topcat,0))
        1

        >>> v = parse(('the pigeons are punished' + ( ' and they suffer' * 2)).split(), use_features=True, print_trees=False, return_chart=True)
        >>> v.count(v.solutions(v.topcat,0))
        2

        
        >>> v = parse(('the pigeons are punished' + ( ' and they suffer' * 3)).split(), use_features=True, print_trees=False, return_chart=True)
        >>> v.count(v.solutions(v.topcat,0))
        5

        >>> v = parse(('the pigeons are punished' + ( ' and they suffer' * 4)).split(), use_features=True, print_trees=False, return_chart=True)
        >>> v.count(v.solutions(v.topcat,0))
        14

        >>> v = parse(('the pigeons are punished' + ( ' and they suffer' * 5)).split(), use_features=True, print_trees=False, return_chart=True)
        >>> v.count(v.solutions(v.topcat,0))
        42

        >>> v = parse(('the pigeons are punished' + ( ' and they suffer' * 6)).split(), use_features=True, print_trees=False, return_chart=True)
        >>> v.count(v.solutions(v.topcat,0))
        132

        >>> v = parse(('the pigeons are punished' + ( ' and they suffer' * 7)).split(), use_features=True, print_trees=False, return_chart=True)
        >>> v.count(v.solutions(v.topcat,0))
        429

        """
        if not hasattr(self,'_traced'):
            self.trace_edges()
        return self._traced[e]



  

    def somepartials(self,right=None,left=None,label=None,first=None,rest=None):
        """
        Accessor that gets a set of relevant partials.
        """

        if right is not None:
            r = self.partials[right]
        else:
            r = set().union(*self.partials)
        if left is not None:
            r = {e for e in r if e.left==left}
        if label is not None:
            r = {e for e in r if self.compat(e.label,label)}
        if first is not None:
            r = {e for e in r if self.compat(e.needed[0],first)}
        if rest is not None:
             r = {e for e in r if self.allcompatible(e.needed[1:],rest)}
        return frozenset(r)

    def trees(self, e):
        """
        Generate the trees that are rooted in edge.

        Parameters
        ==========

        e: Edge
            the chart entry whose daughters we trace.

        This is an iterator, and can unpack the first few of even very
        ambiguous parse forests. The following is too costly to run as 
        a doctest, but does work.

        from math import log10
        v = chart.parse(('the pigeons are punished' + ( ' and they suffer' * 152)).split(),return_chart=True, 
                print_trees=False,show_chart=False)
        print log10(v.trace_edges())
        87.98857337128997
        ts = v.trees(v.solutions(v.topcat)[0])
        print len((treestring(ts.next()))
        16522
        """
    

        prev = self.get_prev(e)
        if prev:
            for c in prev:
                for p in self.somepartials(right=c.left,left=e.left,label=e.label,first=c.label,rest=e.needed):
                   for left in self.trees(p):
                        for right in self.trees(c):
                            yield Tree(e.label,left.children + tuple([right]))
        else:
            yield Tree(e.label)

    def results(self, show_chart=False,trace_edges=False,**kwds):
        """
        Code for creating results.
        """
        return dict(sols=self.solutions(self.topcat),
                    n_trees=self.trace_edges(),
                    topcat=self.topcat)
        






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
    def __str__(self):
        """
        >>> print Tree("S",[Tree("NP"),Tree("VP")])
        S
         NP
         VP
        <BLANKLINE>
        """
        return treestring(self)
    


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


def parse(sentence, verbose=False, topcat='S', grammar=GRAMMAR,sep=' ', input_source=LinearWords, 
            use_features=False,show_chart=False,print_trees=True,return_chart=False,
            trace_edges=True,
            return_trees = False):
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
        grammar = features.make_feature_grammar()
        topcat = icat.from_string(topcat)


    v = Chart(sentence, verbose=verbose,grammar=grammar,input_source=input_source, using_features=use_features)
    v.topcat = topcat
    sols = v.solutions(topcat)

    res = v.results(show_chart=show_chart,
                    print_trees=print_trees, 
                    trace_edges=trace_edges)



    silent = not (print_trees or show_chart)
    if not silent:
        print sentence

    if show_chart:
        v.show()

    if print_trees:
        i = 0
        for e in sols:
            for tree in v.trees(e):
                i += 1
                if print_trees:
                    print "Parse %d:" % i
                    print treestring(tree, tab=0, sep=sep),

    if not silent:
        if res['n_trees'] == 0:
            print "No parse"
        else:
            print res['n_trees'], "parses"

    if return_chart:
        return v
    else:
        return None


def edge_summary(v):
    """
    Summarize the contents of the chart. 
    >>> v = parse(["the","pigeons","suffer"],return_chart=True)
    ['the', 'pigeons', 'suffer']
    Parse 1:
    S
     Np
      det the
      Nn
       n pigeons
     Vp
      v suffer
    1 parses
    >>> edge_summary(v)
    {'partials': 31, 'completes': 12}
    """
    ps = set().union(*v.partials)
    cs = set().union(*v.completes)
    ps_no_pred = {p for p in ps if p not in v.prev}

    cs_no_pred = {p for p in cs if p not in v.prev}
    assert len(cs_no_pred) == 0
    assert len(ps_no_pred) == 0
    return dict(partials= len(ps),completes=len(cs))
    







    
      
    



