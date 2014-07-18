Chartparse
==========

This is a bottom-up chart parser for a fragment of English.
It uses the active chart datastructure. The design is based
on Steve Isard's LIB CHART [1]_, a teaching tool (written in 1983) that
comes with the wonderful Poplog AI development environment [1]_.

The key data structures are containers for partial and complete edges, called
partials and completes below. Completes is an array of sets such that all the
edges starting at position <code>i</code> of the input string are stored in
`completes[i]`. Partials is the same, except that `partial[i]`
stores all the edges that **end**  at `i`. This layout is designed
to make application of the fundamental rule of chart parsing transparent.

Some additions have been made to the grammar to allow commands to an imaginary movie system, and
input as if from a lattice.


There are versions in Java (not currently actively developed), and Python.
See the README files in those directories for details.

.. _[1] http://www.poplog.org/
.. _[2] http://www.poplog.org/gospl/packages/pop11/lib/chart.p

.. moduleauthor: Chris Brew

	
