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
		return ImmutableCategory(self.cat,tuple(d.items()))

	def extendc(self, constrain_keys, category):
		c = self
		for k in constrain_keys:
			v = category.getfeat(k, None)
			if v:
				c = c.extend(k,v)
		return c





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
			return ImmutableCategory(cat=xx,features=None)


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
		return tuple([tuple(f.split(':')) for f in fs if ':' in f])

	@staticmethod 
	def fcheck(c1,c2):
		ff1 = c1.features
		ff2 = c2.features

		if (not ff1) or (not ff2):
			return True

		fkeys1,fvals1 = zip(*ff1)
		fkeys2,fvals2 = zip(*ff2)
		
		for i,f1 in enumerate(fkeys1):
			try:
				v2 = fvals2[fkeys2.index(f1)]
				v1 = fvals1[i]
				if v1 != v2:
					return False
			except:
				pass
		return True



	



class Category(namedtuple("Category",("cat","features"))):
	"""
	A syntactic category, with features. 

	XXX should be immutable.

	"""

	def __repl__(self):
		"""
		"""
		if len(self.features) == 0:
			return "{cat}".format(cat=self.cat)
		else:
			return "{cat}({fs})".format(cat=self.cat,fs=self.fspec)

	def as_string(self, features=True):
		cat = "{cat}".format(cat=self.cat)
		if features:
			cat += self.afeats_string()
		return cat

	def afeats_string(self):
		if self.atomic_features:
					return "({fs})".format(fs=",".join(sorted([("{f}:{v}").format(f=f,v=v) 
														for f,v in self.features.items()
														if v is not None])))
		else:
			return ""

	def cs_string(self):
		if self.compiled_constraints:
			return " {cs}".format(cs=self.compiled_constraints)
		else:
			return ""


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
	
		XXX this is a confusion. Constraints
		live on rules, though they are SPECIFIED on categories.
		"""
		return frozenset({f for f in self.features 
				if self.features[f] is None})

	
	@property
	def atomic_features(self):
		"""
		The atomic features on the category.
		
		>>> c = Category.from_string('Np(case:subj,num)')
		>>> c.atomic_features
		{'case': 'subj'}
		"""
		return {f:v for f,v in self.features.items() 
				if self.features[f] is not None}
	@property
	def fspec(self):
		return ",".join(sorted([("{f}" if v is None else "{f}:{v}").format(f=f,v=v) for f,v in self.features.items()]))
		




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


		"""

		lhsc = ImmutableCategory.constraints(lhs)
		rhsc = tuple([ImmutableCategory.constraints(r) for r in rhs])
		keys = lhsc.union(*rhsc)
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

	

		




	


class FeatureizedRule(namedtuple('FeatureizedRule',('lhs','rhs'))):
	"""One production of a context-free grammar.


	Attributes
	----------
	lhs: ImmutableCategory
		The left hand side of the rule.
	rhs: list [ImmutableCategory]
	The right hand side of the rule.
	constraints: Constraints
		the compiled constraints on the rule.

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

	def __repr__(self):
		return self.as_string(constraints=True,features=True)
		

	def as_string(self,features=True,constraints=True):
		if constraints and self.compiled_constraints:
			return "{lhs} -> {rhs} {constraints}".format(lhs=self.lhs.as_string(),
														constraints = self.compiled_constraints,
														rhs=" ".join([r.as_string() for r in self.rhs]))
		else:
			return "{lhs} -> {rhs}".format(lhs=self.lhs.as_string(),
				rhs=" ".join([r.as_string() for r in self.rhs]))


	@property
	def constraints(self):
		return frozenset(self.lhs.constraints.union(*[r.constraints for r in self.rhs]))

	@property 
	def compiled_constraints(self):
		"""
		Return a representation of the non-trivial constraints on the
		rule. The test for len > 1 is there because the grammar 
		expansion can produce productions where the only mention of
		the constrained feature is on lhs. These are non-ops, so we
		suppress them.

	
		"""
		return  Constraints([(c,self._nc(c))
							for c in self.constraints 
							if len(self._nc(c)) > 1 ])




	def _nc(self,c):
		r = set()
		if c in self.lhs.constraints:
			r.add(0)
		for i,x in enumerate(self.rhs):
			if c in x.constraints:
				r.add(i+1)

		return frozenset(r)


	@staticmethod
	def grammar_from_string_pairs(string_pairs):
		"""
		expand a grammar from 
		"""
		return [FeatureizedRule(x,y) for x,y in string_pairs]



	@staticmethod
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

class Grammar:
	def __init__(self, rules, state=None):
		self.state = (npr.RandomState(42) if state is None else state)
		self.grammar = rules

def make_feature_grammar():
	return Grammar(list(compile_grammar(english.RULES)) + list(compile_lexicon(english.WORDS)))




