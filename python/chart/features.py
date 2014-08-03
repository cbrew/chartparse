"""
A feature system for chart parsing
==================================

This feature system supports parsing with atomic feature values. It allows 
feature specifications of two types:

	- specification of a given value. This is a colon-separated pair, such as ``num:pl``. When
	  found in a lexical category or on the left-hand side of a rule, it asserts that
	  the category has that value. When found on the right-hand side of the rule it
	  imposes a requirement that the category in question should not conflict with
	  that feature.

	 - specification of a re-entrancy. This is a single feature value, such as ``num``. It can
	   only occur in a rule. When found there, it enforces a consistency requirement, requiring
	   that the feature be instantiated to the same value everywhere that the re-entrancy specification
	   occurs. For efficiency, this consistency check is only partially enforced: feature values are 
	   propagated "upwards" (i.e. from right-hand side to left-hand side) but not "downwards" (from 
	   left-hand side to right hand side). That is, if we have the rule

		::

		S (num) -> Np(num case:subj) Vp(num)

		and we instantiate it with a plural ``Np(num:pl)``, such as "the pigeons", we will make sure 
		that the `Vp` that completes the sentence (which might be "suffer") will also be compatible
		with plural. This will allow "the pigeons suffer" and "the pigeons suffered", but not 
		"the pigeons suffers", which fails because "suffers" is unambiguously `v(num:sing)`. Both
		legal sentences will be marked as plural, and ``S(num:pl)`` will be entered into the chart
		on their completion.

		However, when we go through the same process with a different noun phrase such as "the sheep",
		for which the number is uncertain, things happen differently. In that case, the noun phrase
		will have category ``Np``, so the parser will have no particular expectation about the number of
		the following verb phrase, and all three of "the sheep suffer", "the sheep suffers" and "the 
		sheep suffers" will be accepted.

		Internally, the constraints on a rule are represented as a map from feature names to sets of 
		indices, where the index of the parent node is 0, followed by indices for those child nodes
		that carry the feature. Also, alternate right-hand sides are expanded into simple rules with
		a single right-hand side.


    	>>> chart.parse(['the','sheep','suffers'],sep='_', use_features=True)
    	['the', 'sheep', 'suffers']
    	Parse 1:
    	S(num:sing)
    	_Np
    	__det the
    	__Nn
    	___n sheep
    	_Vp(num:sing)
    	__v(num:sing,tr:intrans) suffers
    	1 parses
	

    	>>> chart.parse(['the','sheep','suffer'],sep='_', use_features=True)
    	['the', 'sheep', 'suffer']
    	Parse 1:
    	S(num:pl)
    	_Np
    	__det the
    	__Nn
    	___n sheep
    	_Vp(num:pl)
    	__v(num:pl,tr:intrans) suffer
    	1 parses

    	>>> chart.parse(['the','sheep','suffered'],sep='_', use_features=True)
    	['the', 'sheep', 'suffered']
    	Parse 1:
    	S
    	_Np
    	__det the
    	__Nn
    	___n sheep
    	_Vp
    	__v(tr:intrans) suffered
    	1 parses

    	>>> chart.parse(['the','pigeon','suffer'],sep='_', use_features=True)
    	['the', 'pigeon', 'suffer']
    	No parse

    	>>> chart.parse(['the','pigeon','suffered'],sep='_', use_features=True)
    	['the', 'pigeon', 'suffered']
    	Parse 1:
    	S(num:sing)
    	_Np(num:sing)
    	__det the
    	__Nn(num:sing)
    	___n(num:sing) pigeon
    	_Vp
    	__v(tr:intrans) suffered
    	1 parses

    	>>> chart.parse(['the','pigeon','suffers'],sep='_', use_features=True)
    	['the', 'pigeon', 'suffers']
    	Parse 1:
    	S(num:sing)
    	_Np(num:sing)
    	__det the
    	__Nn(num:sing)
    	___n(num:sing) pigeon
    	_Vp(num:sing)
    	__v(num:sing,tr:intrans) suffers
    	1 parses


"""
import chart
from collections import namedtuple
import re
import english
import numpy.random as npr




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
			return frozenset(self.features) > frozenset(c.features)



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



		# if not ff1 or not ff2:
		#	return True

		


		# Use the symmetric difference operator
		# to find the feature/value pairs 
		# that are not shared
		unshared = ff1 ^ ff2

		# if the keys are all disjoint,
		# unshared will be the same length
		# as the dict built on it. Otherwise
		# unshared will be longer.
		return len(dict(unshared)) == len(unshared)




class ImmutableRule(namedtuple('ImmutableRule',('lhs','rhs',"constraints"))):
	"""
	A rule made of immutable categories, that is itself immutable.
	
	"""
	def __repr__(self):
		if len(self.constraints) == 0:
			return "{lhs} -> {rhs}".format(lhs=self.lhs,rhs=" ".join(map(str,self.rhs)))
		else:
			return "{lhs} -> {rhs} {cs}".format(cs=self.constraint_strings,lhs=self.lhs,rhs=" ".join(map(str,self.rhs)))

	@staticmethod
	def _cc(lhs, rhs):
		"""
		Return a representation of the non-trivial constraints on the
		rule.

		The constraints are a projection of the lhs and rhs. 

		Caution: the grammar is written in such a way that the
		lhs may have constraints listed that are not in the rhs.
		These are to be dropped.

		Happens with S(num) -> S conj S, which is to be interpreted 
		as S -> S conj S

		"""

		lhsc = ImmutableCategory.constraints(lhs)
		rhsc = tuple([ImmutableCategory.constraints(r) for r in rhs])

		keys = frozenset().union(*rhsc)
		if keys:
			return (lhsc,rhsc)
		else:
			return None

	@property
	def constraint_strings(self):
		return "{{lhs={lhs},rhs={rhs}}} ".format(lhs=",".join(sorted(self.constraints[0])),
													 rhs=[",".join(sorted(r)) for r in self.constraints[1]])


	def __new__(cls,lhs,rhs):
		left = ImmutableCategory.from_string(lhs)
		
		right = tuple([ImmutableCategory.from_string(r) for r in rhs])

		


		return super(ImmutableRule, cls).__new__(cls, lhs=left, 
													rhs=right, 
													constraints=ImmutableRule._cc(lhs,rhs))


def string_pairs_from_rules(spec):
		"""
		Create a set of string pairs from rules.

		"""
		lines = spec.split('\n')
		for line in lines:
			lhs,rhses = line.split('->')
			lhs = lhs.strip()
			for rhs in rhses.split('|'):
				yield lhs,rhs.split()

def grammar_from_string_pairs(string_pairs):
		"""
		expand a grammar from 
		"""
		return [ImmutableRule(x,y) for x,y in string_pairs]

def compile_grammar(spec):
	"""
	Read the grammar and featureize it.

	
	"""
	sp = string_pairs_from_rules(english.RULES)
	return grammar_from_string_pairs(sp)


def compile_lexicon(spec):
	"""
	Read the lexicon and put into the form of featureized rules. 
	Use the same datastructure as for the CFG rules, except that
	the rhs is a single string.

	Note: the format for the lexicon is more rigid than is ideal,
	and intolerant of extra/missing whitespace. Fixable, but hardly
	worth fixing.
   

	"""
	lines = spec.split('\n')
	for line in lines:
		a = line.split()
		key = a[0]
		cats = []
		for x in a[1:]:
			if x == '|':
				pass
			elif '|' in x:
				for y in x.split('|'):
					if y:
						cats.append(y)
			else:
				cats.append(x)
		for cat in cats:
			yield ImmutableRule(lhs=cat,rhs=[key])

import networkx as nx

class Grammar:
	def __init__(self, rules, state=None):
		self.state = (npr.RandomState(42) if state is None else state)
		self.grammar = rules
		self.left_corner = self._make_left_corner()
	def _make_left_corner(self):
		g = nx.DiGraph()
		for r in self.grammar:
			g.add_edge(r.lhs,r.rhs[0])
		return nx.freeze(g)




def make_feature_grammar():
	return Grammar(list(compile_grammar(english.RULES)) + list(compile_lexicon(english.WORDS)))




