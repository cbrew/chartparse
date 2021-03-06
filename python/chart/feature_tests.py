"""
feature tests
=============

We need to be sure that the chart does the right thing
with complex categories. Specifically, if we have a
bare determiner 

::code

	det

in some cell of the chart, and an edge proposed adding

::code

	det(num:sing)

we should not do so, since that is duplicative. Equally, when we 
add ``det(num:sing)``, then propose adding ``det``, we should 
replace the less general with the more general.

We also want to make sure that feature percolation works as 
expected. The intention is that a feature name mentioned
in more than one place in a rule will result in propagation
of any feature value found, both from a child node to any
labeled later siblings and from child node to the parent, if 
the parent is labeled. We never propagate from later siblings
to earlier siblings, because chart parsing is built on the 
assumption that nodes will not become more specific after they
are entered into the chart.

"""

import chart
from features import ImmutableCategory as icat
from features import make_feature_grammar
import time


def too_expensive(): # pragma:no cover
	 from math import log10
	 sentence = ('the pigeons are punished' + ( ' and they suffer' * 152)).split()
	 print 'sentence of length',len(sentence)
	 start = time.clock()
	 v = chart.parse(sentence,return_chart=True, 
                		print_trees=False,show_chart=False)
	 end = time.clock()
	 print "Took",(end - start),"seconds"
	 print "Counting trees"
	 start = time.clock()
	 print "Log of number of trees",log10(v.trace_edges())
	 end = time.clock()
	 print "Took",(end - start),"seconds"
	 print 'By best estimate this is many more trees than there are atoms in the universe'
	 ts = v.trees(v.solutions(v.topcat)[0])
	 tree = chart.treestring(ts.next())
	 print 'First tree has length',len(tree),'characters'
	 print tree[:40],'...\n',tree[10000:10100],'...\n',tree[-80:]
	 for i in range(199):
	 	tree = chart.treestring(ts.next())
	 print '200th tree has length',len(tree),'characters'
	 print tree[:40],'...\n',tree[10000:10100],'...\n',tree[-80:]

def test_subsumption():
	"""
	>>> chart.parse(['pigeons'], use_features=True,topcat='Nn(num:pl)')
	['pigeons']
	Parse 1:
	Nn(num:pl)
	 n(num:pl) pigeons
	1 parses

	>>> ch = chart.Chart(['pigeons'], grammar=make_feature_grammar(),using_features=True)
	>>> len(ch.completes[0])
	4

	>>> ch = chart.Chart(['pigeons'], grammar=make_feature_grammar(),using_features=True)
	>>> ch.completes[0]
	set([C(Pn, 0, 1), C(n(num:pl), 0, 1), C(Nn(num:pl), 0, 1), C(pigeons, 0, 1)])


	Adding an edge that is already there should be a non-op
	>>> ch = chart.Chart(['pigeons'], grammar=make_feature_grammar(),using_features=True)
	>>> ch.incorporate(list(ch.completes[0])[0])
	>>> len(ch.completes[0])
	4
	
	Adding an edge that is more specific than one already there should be a non-op
	>>> ch = chart.Chart(['pigeons'], grammar=make_feature_grammar(),using_features=True)
	>>> edge = chart.Edge(label=icat.from_string('n(num:pl,case:subj)'),left=0,right=1,needed=tuple([]),constraints=None)
	>>> ch.incorporate(edge)
	>>> ch.completes[0]
	set([C(Pn, 0, 1), C(n(num:pl), 0, 1), C(Nn(num:pl), 0, 1), C(pigeons, 0, 1)])


	Adding an edge that is less specific than one already there should result
	in the replacement of the previous edge by the new one, leaving the length
	of the chart unchanged.
	>>> ch = chart.Chart(['pigeons'], grammar=make_feature_grammar(),using_features=True)
	>>> edge = chart.Edge(label=icat.from_string('n'),left=0,right=1,needed=tuple([]),constraints=None)
	>>> ch.incorporate(edge)
	>>> len(ch.completes[0])
	4

	>>> ch = chart.Chart(['pigeons'], grammar=make_feature_grammar(),using_features=True)
	>>> edge = chart.Edge(label=icat.from_string('n'),left=0,right=1,needed=tuple([]),constraints=None)
	>>> ch.incorporate(edge)
	>>> ch.completes[0]
	set([C(Pn, 0, 1), C(Nn(num:pl), 0, 1), C(pigeons, 0, 1), C(n, 0, 1)])

	>>> ch = chart.Chart(['the','pigeons','are','punished'], grammar=make_feature_grammar(),using_features=True)
	>>> ps =  sorted(ch.partials[2])
	>>> edge = sorted(ch.partials[2])[-3]
	>>> edge
	P(S(num:pl), 0, 2,(Vp(num:pl),))
	>>> ch.incorporate(edge)
	>>> ps == sorted(ch.partials[2])
	True
	

	Make sure we can build a partial edge ourselves and that incorporating it is a non-op	
	>>> ch = chart.Chart(['the','pigeons','are','punished'], grammar=make_feature_grammar(),using_features=True)
	>>> ps =  sorted(ch.partials[2])
	>>> edge=chart.Edge(label=icat.from_string('S(num:pl)'),left=0,right=2,needed=tuple([icat.from_string('Vp(num:pl)')]),constraints=None)
	>>> ch.incorporate(edge)
	>>> ps == sorted(ch.partials[2])
	True

	Make sure we can build a partial edge ourselves differing only in needed field, less general
	>>> ch = chart.Chart(['the','pigeons','are','punished'], grammar=make_feature_grammar(),using_features=True)
	>>> ps =  sorted(ch.partials[2])
	>>> edge=chart.Edge(label=icat.from_string('S(num:pl)'),left=0,right=2,needed=tuple([icat.from_string('Vp(num:pl,case:subj)')]),constraints=None)
	>>> ch.incorporate(edge)
	>>> ps == sorted(ch.partials[2])
	True
	>>> sorted(ch.partials[2])[7]
	P(S(num:pl), 0, 2,(Vp(num:pl),))

	Make sure we can build a partial edge ourselves differing only in needed field, more general. Changes set.
	>>> ch = chart.Chart(['the','pigeons','are','punished'], grammar=make_feature_grammar(),using_features=True)
	>>> ps =  sorted(ch.partials[2])
	>>> edge=chart.Edge(label=icat.from_string('S(num:pl)'),left=0,right=2,needed=tuple([icat.from_string('Vp')]),constraints=None)
	>>> ch.incorporate(edge)
	>>> ps == sorted(ch.partials[2])
	False
	>>> sorted(ch.partials[2])[7]
	P(S(num:pl), 0, 2,(Vp,))

	Next one should have a parse because number agreement is not enforced between different branches of
	a conjunction.

    >>> v = chart.parse('stuart suffers and they suffer'.split(),return_chart=True,use_features=True,sep='_')
    ['stuart', 'suffers', 'and', 'they', 'suffer']
    Parse 1:
    S
    _S(num:sing)
    __Np(num:sing)
    ___pn(num:sing) stuart
    __Vp(num:sing)
    ___v(num:sing,tr:intrans) suffers
    _conj and
    _S(num:pl)
    __Np(case:subj,num:pl)
    ___pn(case:subj,num:pl) they
    __Vp(num:pl)
    ___v(num:pl,tr:intrans) suffer
    1 parses
    
    This one should have no number features on the conjoined S.

    >>> v = chart.parse('stuart suffers and stuart suffers'.split(),return_chart=True,use_features=True,sep='_')
    ['stuart', 'suffers', 'and', 'stuart', 'suffers']
    Parse 1:
    S
    _S(num:sing)
    __Np(num:sing)
    ___pn(num:sing) stuart
    __Vp(num:sing)
    ___v(num:sing,tr:intrans) suffers
    _conj and
    _S(num:sing)
    __Np(num:sing)
    ___pn(num:sing) stuart
    __Vp(num:sing)
    ___v(num:sing,tr:intrans) suffers
    1 parses

	



	"""