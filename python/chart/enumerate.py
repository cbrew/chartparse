"""
Enumerate trees from a chart. Solutions are produced in order of the number of edges traversed. 

A tree is a solution if all its leaves are lexical. 



"""

def safe_trees(chart):
	for x in chart.solutions(chart.topcat):
		for (y,z) in chart.coprev(x):
			yield [(y,z),x]