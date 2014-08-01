import sys
import os
sys.path.append(os.getcwd())
import chart

#
# This sentence has a very large number of parses
##

chart.parse(('the pigeons are punished' + (' and they suffer' * 80)).split(), use_features=True,print_trees=False)