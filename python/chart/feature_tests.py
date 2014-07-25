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

"""

import chart
from features import ImmutableCategory as icat
from features import make_feature_grammar

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
	>>> list(ch.completes[0])[0]
	C(n(num:pl), 0, 1)


	Adding an edge that is already there should be a non-op
	>>> ch = chart.Chart(['pigeons'], grammar=make_feature_grammar(),using_features=True)
	>>> ch.incorporate(list(ch.completes[0])[0])
	>>> len(ch.completes[0])
	4
	
	Adding an edge that is more specific than one already there should be a non-op
	>>> ch = chart.Chart(['pigeons'], grammar=make_feature_grammar(),using_features=True)
	>>> edge = chart.Edge(label=icat.from_string('n(num:pl,case:subj)'),left=0,right=1,needed=tuple([]),constraints=None)
	>>> ch.incorporate(edge)
	>>> list(ch.completes[0])[0]
	C(n(num:pl), 0, 1)


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
	>>> list(ch.completes[0])[0]
	C(n, 0, 1)


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

	



	"""