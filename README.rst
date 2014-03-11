OSU NLP Group's Didactic Chart Parser
=====================================

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

.. _[1] http://www.poplog.org/
.. _[2] http://www.poplog.org/gospl/packages/pop11/lib/chart.p

.. moduleauthor: Chris Brew


Java prerequisites
===================

** Maven
** Java 6

Java build and run
------------------

.. code-block

cd java
mvn package
java -jar target/ChartParser-1.0-SNAPSHOT.jar

Output: (only an extract is shown)
---------------------------------

.. code-block

1:the:0-1
2:pigeons:1-2
3:suffer:2-3
4:det:0-0/[the]
5:n:1-1/[pigeons]
6:v:2-2/[suffer]
7:det:0-1
8:n:1-2
9:v:2-3
10:Np:0-0/[det, Nn]

Tree: 4

(S
 (Np
  (Np
   (det the)
   (Nn
    (n boys)))
  (conj and)
  (Np
   (det the)
   (Nn
    (n girls))))
 (Vp
  (v punish)
  (Np
   (Np
    (det the)
    (Nn
     (n pigeons)))
   (Pp
    (prep in)
    (Np
     (Np
      (det the)
      (Nn
       (adj red)
       (n cages)))
     (Pp
      (prep in)
      (Np
       (det the)
       (Nn
        (adj green)
        (n house)))))))))

Python prerequisites
--------------------

* Python 2.7
* Sphinx for the documentation
	
