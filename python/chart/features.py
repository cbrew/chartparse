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

		>>> chart.parse(['the','sheep','suffers'],sep='_')
		['the', 'sheep', 'suffers']
		Parse 1:
		S
		_Np
		__det the
		__Nn
		___n sheep
		_Vp
		__v suffers
		1 parses

    	>>> chart.parse(['the','sheep','suffer'],sep='_')
    	['the', 'sheep', 'suffer']
    	Parse 1:
    	S
    	_Np
    	__det the
    	__Nn
    	___n sheep
    	_Vp
    	__v suffer
    	1 parses

    	>>> chart.parse(['the','sheep','suffered'],sep='_')
    	['the', 'sheep', 'suffered']
    	Parse 1:
    	S
    	_Np
    	__det the
    	__Nn
    	___n sheep
    	_Vp
    	__v suffered
    	1 parses

    	>>> chart.parse(['the','pigeon','suffer'],sep='_')
    	['the', 'pigeon', 'suffer']
    	No parse

    	>>> chart.parse(['the','pigeon','suffered'],sep='_')
    	['the', 'pigeon', 'suffered']
    	Parse 1:
    	S
    	_Np
    	__det the
    	__Nn
    	___n pigeon
    	_Vp
    	__v suffered
    	1 parses

    	>>> chart.parse(['the','pigeon','suffers'],sep='_')
    	['the', 'pigeon', 'suffers']
    	Parse 1:
    	S
    	_Np
    	__det the
    	__Nn
    	___n pigeon
    	_Vp
    	__v suffers
    	1 parses


"""
import chart
from collections import namedtuple
import re

COMPLEX_CATEGORY=re.compile(r"(\w*)\s*\(([^)]+)\)")

class Category(namedtuple("Category",("cat","features"))):
	@staticmethod
	def from_string(xx):
		if '(' in xx:
			m = COMPLEX_CATEGORY.match(xx)
			assert m,xx
			cat,fs=m.groups()
			return Category(cat=cat, features=Category._feats(fs))

		else:
			return Category(cat=xx,features={})
	@staticmethod
	def _feats(fs):
		return dict([Category._feat(z.strip()) for z in fs.split(',') if z])
	@staticmethod
	def _feat(fs):
		if ":" in fs:
			f,v = fs.split(':')
			return f,v
		else:
			return fs,None

	@property
	def constraints(self):
		"""
		The constraints on the category.
		"""
		return frozenset({f for f in self.features if self.features[f] is None})
	
	@property
	def atomic_features(self):
		"""
		The atomic features on the category.
		"""
		return {f:v for f,v in self.features.items() if self.features[f] is not None}




class FeatureizedRule(namedtuple('FeatureizedRule',('lhs','rhs'))):
	"""One production of a context-free grammar.
	Attributes
	----------
	lhs: Category
		The left hand side of the rule.
	rhs: list [Category]
	The right hand side of the rule.

	Examples
	--------
	>>> r = FeatureizedRule('S(num)',('Np(case:subj,num)','Vp(num)'))
	>>> r.constraints
	frozenset(['num'])
	"""

	def __new__(cls,lhs,rhs):
		left = Category.from_string(lhs)
		right = tuple([Category.from_string(r) for r in rhs])
		return super(FeatureizedRule, cls).__new__(cls, lhs=left, rhs=right)

	@property
	def constraints(self):
		return frozenset(self.lhs.constraints.union(*[r.constraints for r in self.rhs]))

	@staticmethod
	def grammar_from_string_pairs(string_pairs):
		"""
		expand a grammar from 
		"""
		return [FeatureizedRule(x,y) for x,y in string_pairs]

	@staticmethod
	def string_pairs_from_spec(spec):
		lines = spec.split('\n')
		for line in lines:
			lhs,rhses = line.split('->')
			lhs = lhs.strip()
			for rhs in rhses.split('|'):
				yield lhs,rhs.split()




