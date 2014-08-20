
from collections import namedtuple
import heapq
from abc import ABCMeta,abstractmethod

Node = namedtuple('Node',('weight', 'data'))

class SearchType(object):
	"""
	Abstract object defining the protocol needed by
	the agenda-based search code below.
	"""
	__metaclass__ = ABCMeta

	@abstractmethod
	def initial_state(self,seed):
		"""
		Take a seed and generate an initial initial state 
		that populates the agenda.
		"""
		pass

	@abstractmethod
	def successors(self, state):
		"""
		Generate the successors of a state.
		"""
		pass

	@abstractmethod
	def is_solution(self,state):
		"""
		Say whether something is a solution.
		"""
		pass


class TreeSearch:
	"""
	Do agenda-based search using the 
	parameters provided by SearchType.

	The agenda 
	"""
	def __init__(self, search_type, seed,debug=False):
		
		self.search = search_type()
		assert isinstance(self.search,SearchType)
		self.seed = seed
		self.debug = debug
	def __iter__(self):
		"""
		Iterate over the nodes defined by the
		search type, starting from seed.
		"""
		search = self.search
		agenda = [search.initial_state(self.seed)]
		heapq.heapify(agenda)
		while len(agenda) > 0:
			if self.debug:
				print agenda
			item = heapq.heappop(agenda)
			if search.is_solution(item):
				yield item
			for successor in search.successors(item):
				heapq.heappush(agenda,successor)

class NumberSearch(SearchType):
	"""
	Makes numbers in several different ways
	"""
	def initial_state(self,seed):
		return seed
	def successors(self,state):
		if state < 10:
			return {state+2,state+3}
		else:
			return set()
	def is_solution(self,state):
		return (state % 5) == 0

import nltk
import string
class WordSearch(SearchType):
	"""
	Implement naive search for words.
	"""
	words = set(nltk.corpus.words.words())
	alphabet = string.lowercase
	def initial_state(self, seed=''):
		return (len(seed),seed)
	def successors(self,state):
		return {(state[0] + 1, (state[1] + c)) for c in WordSearch.alphabet}
	def is_solution(self,state):
		return state[1] in WordSearch.words


def expand(node,vt):
    if isinstance(node,set):
        return set().union(* [expand(n,vt) for n in node])
    if isinstance(node,Edge):
        return {(0,node,p) for p in vt[node]}
    else:
        return {(node[0]+1,node[1],(c,node[2][1])) for c in expand(node[2][0],vt)} | {(node[0]+1,node[1],(node[2][0],c)) for c in expand(node[2][1],vt)}

def fringe(e):
    if isinstance(e,Edge):
        yield e
    else:
        for f in fringe(e[2][0]):
            yield f
        for f in fringe(e[2][1]):
            yield f


def is_solution(node,vt):
    leaves = {k for k in vt if len(vt[k]) == 0}
    fr = set(fringe(node))
    return fr - leaves

def expand_until_solution(node,vt):
    agenda = [node]
    heapq.heapify(agenda)
    while agenda:
        s = expand(heapq.heappop(agenda),vt)
        for w in s:
            if is_solution(w,vt):
                yield w
            heapq.heappush(agenda,w)








		



