"""
Incremental parsing
===================

The main parser implemented in chart.py uses an agenda, which gives flexibility
for scheduling edges. This one, by contrast is incremental, creating all edges
terminating at point k before any edge at k+1 or later.
"""


class IncrementalParser:
	def parse(self, words):



		# init-topdown, predict-topdown, predict-item
		self.initial_prediction()
		for i,word in enumerate(words):
			# complete, combine, scan, scan-bottomup, predict-bottomup
			self.complete_items(i,word)
			# predict-topdown, predict-item, predict-next, predict-next
			self.predict(i, word)


	def predict_items(self, k):
		for e in active_set[k]:
			pass
			

