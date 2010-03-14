OSU NLP Group's Didactic Chart Parser

 This is a bottom-up chart parser for a fragment of English.
 It uses the active chart datastructure. The design is based
 on Steve Isard's <code>LIB CHART</code>, a teaching tool (written in 1983) that
 comes with the wonderful Poplog AI development environment.

 The key datastructures are containers for partial and complete edges, called
 partials and completes below. Completes is an array of sets such that all the
 edges starting at position <code>i</code> of the input string are stored in
 <code>completes[i]</code>. Partials is the same, except that <code>partial[i]</code>
 stores all the edges that <b>end</b> at <code>i</code>. This layout is designed
 to make application of the fundamental rule of chart parsing transparent.

See <a href="http://www.poplog.org/">http://www.poplog.org/</a>
Ssee <a href="http://www.poplog.org/gospl/packages/pop11/lib/chart.p">http://www.poplog.org/gospl/packages/pop11/lib/chart.p </a>

Author Chris Brew


Prerequisites

Maven
Java 6

Build and run:

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





Some problems for the OSU class



2.1) Why doesn't "the pigeons are punished in the green room" produce a complete parse? Compare "the pigeons are punished by the professors",
which does.

2.2) Implement and test the top-down chart parser described in the lecture slides and in chapter 13 of J&M. Measure its performance relative to the
bottom-up implementation that I provide. Here performance is measured in the following way:

    - your implementation must be correct and complete. That is, it must produce all the edges that are necessary in order to build the correct parses
       for each sentence. Remember that some of the sentences the grammar can generate are ambiguous, so having all the edges for just one parse may
       not be enough.
   - if an implementation is correct (the bottom up parser is), the fewer edges the better,

[A solution is in the code provided with the parser]

2.3)  Adjust the interface to the Rules and Chart classes so that the grammar can be read from a text file rather than being hard-coded 
[easy, 10 pts]

Optional (hard) bonus problems

2.4) Implement and test the allParses method in Chart.java. For full credit the method should be able
to enumerate the first few parses in polynomial time even if there are ridiculously many parses in total
 [up to 50 bonus points]

2.5) Devise a strategy for the chart parser that produces the same edges as Earley's algorithm [25 bonus points]

2.6) Implement and test the countParses method in Chart.java [10 bonus points, and a good warmup for 2.4]

Project ideas
========

2.A) Neither the top-down nor the bottom-up parser is optimal. Both hypothesize edges that they need not. Make this notion precise. Research
previous attempts to fix the problem. See if you can devise an alternative approach that, while staying correct, produces fewer edges. Can you 
make guarantees that your approach will always be better according to the criteria of 2.2?
 [Credit for project. This is a research topic]

2.B) As you may have noticed, the features (e.g. num or case:obj) on the preterminals and nonterminals are not passed through to the parser. So "the pigeons is punished by the professors", 
which should not be accepted, is actually fine according to the current system. Fix this by working out how to use the features to make the grammar tighter, then
implementing your solution.
 [Credit for the project. This is not a research topic, but a well-studied puzzle that you could learn a lot by solving]


