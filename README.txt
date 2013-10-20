OSU NLP Group's Didactic Chart Parser

 This is a bottom-up chart parser for a fragment of English.
 It uses the active chart datastructure. The design is based
 on Steve Isard's <code>LIB CHART</code>, a teaching tool (written in 1983) that
 comes with the wonderful Poplog AI development environment.

 The key data structures are containers for partial and complete edges, called
 partials and completes below. Completes is an array of sets such that all the
 edges starting at position <code>i</code> of the input string are stored in
 <code>completes[i]</code>. Partials is the same, except that <code>partial[i]</code>
 stores all the edges that <b>end</b> at <code>i</code>. This layout is designed
 to make application of the fundamental rule of chart parsing transparent.

See <a href="http://www.poplog.org/">http://www.poplog.org/</a>
Ssee <a href="http://www.poplog.org/gospl/packages/pop11/lib/chart.p">http://www.poplog.org/gospl/packages/pop11/lib/chart.p </a>

Author Chris Brew


Prerequisites

Java version

Maven
Java 6

Build and run:

cd java
mvn package
java -jar target/ChartParser-1.0-SNAPSHOT.jar

Output: (only an extract is shown)

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

...

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


Python version:
	Python 2.5.1 or 2.6.6 (tested, other versions may work, Python 3 probably won't)
	Epydoc if you want to generate the documentation.
