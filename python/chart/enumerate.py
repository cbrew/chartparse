"""
Enumerate trees from a chart. Solutions are produced in order of the number of edges traversed. 

A tree is a solution if all its leaves are lexical. 

Incorrect. Use Dijkstra's algorithm to find all pairs shortest paths maybe

"""

from heapq import heappush,heappop
from collections import namedtuple

## 
# A PTree consists of a list of (current) leaves, a count of how many edges are included
# 

PTree = namedtuple('PTree',('n','leaves'))

def expand(ch, pt):
	for i in range(len(pt.leaves)):
		leaf = pt.leaves[i]
		pre = pt.leaves[:i]
		post = pt.leaves[i+1:]
		for p,q in ch.coprev(leaf):
			if p.left == p.right:
				yield PTree(n=pt.n+1,leaves=pre + [q] + post)
			else:
				yield PTree(n=pt.n+2,leaves=pre + [p,q] + post)


def safe_trees(chart):
	agenda = []
	for x in chart.solutions(chart.topcat):
		heappush(agenda,PTree(n=1,leaves=[x]))
		while agenda:
			pt = heappop(agenda)
			if all(map(chart.is_lexical,pt.leaves)):
				yield pt
			else:
				for spt in expand(chart,pt):
					if spt not in agenda:
						heappush(agenda,spt)