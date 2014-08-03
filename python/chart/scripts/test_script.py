import sys
import os
sys.path.append(os.getcwd())
import chart

#
# This sentence has a very large number of parses
##

def s():
	chart.parse(('the pigeons are punished' + (' and they suffer' * 90)).split(), use_features=True,print_trees=False)

def t():
	chart.parse(('the pigeons are punished' + (' and they suffer' * 90)).split(), use_features=False,print_trees=False)

s()
t()