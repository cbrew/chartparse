"""
This is a bottom-up chart parser for a fragment of English.
It uses the active chart datastructure. The design is based
on Steve Isard's B{LIB CHART}, a teaching tool (written in 1983) that
comes with the wonderful Poplog AI development environment
(Details at U{http://www.poplog.org/gospl/packages/pop11/lib/chart.p} and U{http://www.poplog.org})

@Author: Chris Brew
@Date: April 2009
@Copyright: Chris Brew, 2009
@License: GNU GPL v3
@Contact: christopher.brew@gmail.com


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

from english import GRAMMAR
from collections import defaultdict,deque
import doctest



class Edge(object):
    """
    An edge is an assertion about some span of the text. It has a left and right boundary, 
    a label, and a sequence of needs. If it has no needs, it is said to be B{COMPLETE}, otherwise
    it is described as B{PARTIAL}

    @type label: string
    @ivar label: the mother node of the constituent that this edge would represent.
    @type left: integer(0..n)
    @ivar left: the index of the left boundary of the edge.
    @type right: integer(0..n)
    @ivar right: the index of the right boundary of the edge.
    @type needed: tuple of strings
    @ivar needed: strings representing the categories that the edge needs.
    """

    def __init__(self,label,left,right,needed):
        """
        Constructs an edge.

        @type label: string
        @param label: the mother node of the constituent that this edge would represent.
        @type left: integer(0..n)
        @param left: the index of the left boundary of the edge.
        @type right: integer(0..n)
        @param right: the index of the right boundary of the edge.
        @type needed: tuple of strings
        @param needed: strings representing the categories that the edge needs.
        """
        self.label = label
        self.left = left
        self.right = right
        self.needed = needed   
    def iscomplete(self):
        """
        Test if the edge is complete
        """
        return not self.needed 
    def ispartial(self):
        """
        Test if the edge is partial
        """
        return self.needed
    __slots__ = ["label","left","right","needed"]    
    def __repr__(self):
        """
        This method is part of Python's infrastructure for printing. It produces
        a textual description of the Edge. 

        @See: U{http://docs.python.org/reference/datamodel.html#object.__repr__}
        """
        return "Edge(%r,%d,%d,%r)" % (self.label,self.left,self.right,self.needed)

    def __eq__(self,other):
        """
        This method is required if we want to make Edges usable in Python's set and map datastructures. 

        @See: U{http://docs.python.org/reference/datamodel.html#object.__eq__}
        """
        return self.label == other.label and self.left == other.left and self.right == other.right and self.needed == other.needed
    def __hash__(self):
        """
        This method is needed in order to ensure that Edges in sets and maps are hashable and 
        can compare unequal.

        @See: U{http://docs.python.org/reference/datamodel.html#object.__hash__}
        """
        return hash((self.label,self.left,self.right,self.needed))



class Chart(object):
    """An active chart parser.

    @Type partials: list<set<Edge>>
    @Ivar partials: a list of sets Partial edges ending in position i are stored in partials[i]
    @Type completes: list<set<Edge>>
    @Ivar completes: a list of sets Complete edges starting in position i are stored in completes[i]
    @Type prev: defaultdict<set<Edge>>
    @Ivar prev: mapping from edges to the complete edges that gave rise to them: empty for edges not created by fundamental rule
    @Type agenda: deque<Edge>
    @Ivar agenda: The list of edges still remaining to be incorporated.
    """
    def __init__(self,words):
        """
        Create and run the parser

        @Type words: list of string.
        @Param words: the words to be parsed.
        """
        self.partials = [set() for _ in range(len(words)+1)]
        self.completes = [set() for _ in range(len(words)+1)]
        self.prev = defaultdict(set)
        self.agenda = deque()
        for i in range(len(words)):
            self.agenda.append(self.lexical(words[i],i))
        while self.agenda:
            self.incorporate(self.agenda.popleft())

    def lexical(self,word,i):
        """
        Create a lexical edge based on C{word}
        
        @Type word: string
        @Param word: the word to base the edge on
        @Type i: integer
        @Param i: where the edge starts
        """
        return Edge(word,i,i+1,())

    def solutions(self,topCat):
        """
        Find the solutions rooted in C{topCat}
        
        @Type topCat: string
        @Param topCat: the symbol that the sentence should be rooted in.
        @Rtype: list<Edge>
        """
        return [e for e in self.completes[0] if e.right == len(self.completes) - 1 and e.label == topCat]



    def add_prev(self,e,c):
        """
        Record information about the B{COMPLETE} predecessor of an edge Taken together 
        with the edge itself, this lets the B{PARTIAL} partner be reconstructed.

        @Type e: Edge
        @Param e: an edge that has just been made
        @Type c: Edge
        @Param c: the predecessor of e
        """
        self.prev[e].add(c)
        return e
    def get_prev(self,e):
        """
        Return the predcessors of an edge
        
        @Type e: Edge
        @Param e: the edge whose predecessors are desired
        @Rtype: set<Edge>
        @Return: the predecessors of e
        """
        return self.prev[e]


    def pairwithpartials(self,partials,e):
        """
        Run the fundamental rule for everything in C{partials} that goes with C{e}.

        Updates the C{agenda} by adding to its end.

        @Type partials: set<Edge>
        @Param partials: the potential partners of e
        @Type e: Edge
        @Param e: The complete edge that should be completed
        """
        for p in partials:
            if e.label == p.needed[0]:
                self.agenda.append(self.add_prev(Edge(p.label,p.left,e.right,p.needed[1:]),e))

    def pairwithcompletes(self,e,completes):
        """
        Run the fundamental rule for everything in C{completes} that goes with C{e}.

        Updates the C{agenda} by adding to its end.

        @Type completes: set<Edge>
        @Param completes: the potential partners of e
        @Type e: Edge
        @Param e: The partial edge that should be completed
        """
        for c in completes: 
            if e.needed[0] == c.label:
                self.agenda.append(self.add_prev(Edge(e.label,e.left,c.right,e.needed[1:]),c))
        

    def spawn(self,lc,i):
        """
        Spawn empty edges from the rules that match C{lc}.

        @Type lc: string
        @Param lc: the label of the left corner item to spawn from.
        @Type i: integer
        @Param i: the index of the cell where the empty edges are to go.
        """
        for (lhs,rhs) in GRAMMAR: 
            if rhs[0] == lc:
                self.agenda.append(Edge(lhs,i,i,tuple(rhs)))
        

    def incorporate(self,e):
        """
        Add C{e} to the chart and trigger all corresponding actions.

        @Type e: Edge
        @Param e: the edge to be added
        """
        if e.iscomplete():
            if e not in self.completes[e.left]:
                self.completes[e.left].add(e)
                self.spawn(e.label,e.left)
                self.pairwithpartials(self.partials[e.left],e)
        elif e.ispartial():
            if e not in self.partials[e.right]:
                self.partials[e.right].add(e)
                self.pairwithcompletes(e,self.completes[e.right])
        else:
            raise "Huh? edge has to be either partial or complete!"

    def trees(self,e):
        """
        Generate the trees that are rooted in edge.
        
        @Type e: Edge
        @Param e: the chart entry whose daughters we trace
        @See: U{http://www.ibm.com/developerworks/library/l-pycon.html} for a good 
        explanation of Python generators, which are used here.
        """
        prev = self.get_prev(e)
        if prev:
            for c in prev:
                for p in self.partials[c.left]:
                    if p.needed[0] == c.label and p.label == e.label and p.left == e.left and p.needed[1:] == e.needed:
                        for left in self.trees(p):
                            for right in self.trees(c):
                                yield Tree(e.label,left.children+tuple([right]))
        else:
            yield Tree(e.label)


class Tree(object):
    """
    Container for syntax trees.

    @Type parent: string
    @Ivar parent: label of parent node
    @Type children: tuple<Tree>
    @Ivar children: the subtrees (possibly empty).
    """
    def __init__(self,parent,children=()):
        self.parent = parent
        self.children = children
    __slots__ = ["parent","children"]

def treestring(t,tab = 0):
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
        s = (' '*tab)  + t.parent + ' ' + t.children[0].parent + '\n'
    else:
        s = (' '*tab)  + t.parent + '\n'
        for child in t.children:
            s += treestring(child,tab+1)
    return s
    
def parse(sentence):
    """
    Print out the parses of a sentence

  
    @Type sentence: list<string>
    @Param sentence: the words to be parsed
    """
    v = Chart(sentence)
    print sentence
    i = 0
    for e in v.solutions('S'):
        for tree in v.trees(e):
            i+= 1
            print "Parse %d:" % i
            print treestring(tree),
    print i,"parses"

if __name__ == "__main__":
    doctest.testmod()

#    parse(["the","pigeons",'are','punished','and','they','suffer'])
#    parse(["the",'scientists','program','the','computers'])
#    parse(["the",'scientists','program','the','enormous','computers','in','the','green','room'])
#    parse(["the",'scientists','program','the','enormous','computers','in','the','red','cage',"in","the","green","room"])
#    parse(["the",'scientists','program','the','enormous','computers','in','the','red','cage',"in","the","green","room","in","the","blue","house"])

            
            
   
    
