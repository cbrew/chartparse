/*
 *
 *    Copyright [2010] Chris Brew
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 */
package edu.osu.nlp.chartparser;

import java.lang.reflect.Constructor;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;
import java.util.ResourceBundle;
import java.util.Set;
import java.util.TreeSet;

/**
 * CSE 732 Chart Parser
 * This is a bottom-up chart parser for a fragment of English.
 * It uses the active chart datastructure. The design is based
 * on Steve Isard's <code>LIB CHART</code>, a teaching tool
 * (written in 1983) that comes with the wonderful Poplog
 * AI development environment.
 *
 * The key datastructures are containers for partial and complete edges, called
 * partials and completes below. Completes is an array of sets such that all the
 * edges starting at position <code>i</code> of the input string are stored in
 * <code>completes[i]</code>. Partials is the same, except that
 *  <code>partial[i]</code>
 * stores all the edges that <b>end</b> at <code>i</code>. This layout is
 * designed to make application of the fundamental rule of chart parsing
 * transparent.
 *
 * @see <a href="http://www.poplog.org/">http://www.poplog.org/</a>
 * @see <a href="http://www.poplog.org/gospl/packages/pop11/lib/chart.p">
 * chart.p </a>
 * @author Chris Brew
 */
public class Chart {

    /**
     * tracks statistics for complete edges.
     */
    private int numCompleteEdges = 0;

    /**
     * accessor for number of complete edges.
     * @return number of complete edges
     */
    public final int getNumCompleteEdges() {
        return numCompleteEdges;
    }
    /**
     * tracks statistics for partial edges.
     */
    private int numPartialEdges = 0;

    /**
     * accessor for number of partial edges.
     * @return number of partial edges
     */
    public final int getNumPartialEdges() {
        return numPartialEdges;
    }
    /**
     * will be set to a class that provides a strategy.
     */
    private Strategy strategy = null;
    /**
     * may be set to a class that tracks the arrival of edges.
     */
    private EdgeMonitor monitor = null;
    /**
     * controls the strategy adopted by the chart parser.
     *
     */
    private boolean bottomUp = true;
    /**
     * the length of the input string.
     */
    private final int numWords;
    /**
     * store for agenda.
     */
    private final Queue<Edge> agenda;
    /**
     * store for complete edges.
     */
    private final ArrayList<Set<Edge>> completes;
    /**
     * store for partial edges.
     */
    private final ArrayList<Set<Edge>> partials;
    /**
     * the grammar used.
     */
    private final List<Rule> rules;
    /**
     * the sentence being parsed.
     */
    private String[] sentence;

    /**
     * Implements a chart parser.
     * @param words the words to be parsed
     * @param topCats the allowed root categories
     */
    public Chart(final String[] words, final Set<String> topCats) {
        ResourceBundle bundle = ResourceBundle.getBundle("Chart");
        String grammarFile = bundle.getString("parser.grammar");

        bottomUp = bundle.getString("parser.bottomUp").equals("true");

        try {
            if (bundle.getString("parser.monitorEdges").equals("true")) {
                Class<?> consClass =
                        Class.forName(bundle.getString("parser.monitorClass"));
                Class<?>[] argClasses = {};
                Object[] args = {};
                Constructor<?> cons =
                        (Constructor<?>) consClass.getConstructor(argClasses);

                monitor = (EdgeMonitor) cons.newInstance(args);
            }
        } catch (Exception e) {
            System.out.println("Failed to find edge monitor class"
                    + " as configured: exiting!");
            System.exit(-1);
        }

        numWords = words.length;
        completes = new ArrayList<Set<Edge>>(numWords + 1);
        partials = new ArrayList<Set<Edge>>(numWords + 1);
        sentence = words;
        agenda = new LinkedList<Edge>();

        // read rules from grammar file.
        if (bundle.getString("parser.useInternalGrammar").equals("true")) {
            rules = Rules.english();
        } else {
            rules = Rules.grammar(grammarFile);
        }

        for (int i = 0; i <= numWords; i++) {
            completes.add(new TreeSet<Edge>());
            partials.add(new TreeSet<Edge>());
        }

        if (bottomUp) {
            strategy = new BottomUpStrategy(this);
        } else {
            strategy = new TopDownStrategy(this);
        }

        strategy.initialize(words, topCats);

        while (!(agenda.isEmpty())) {
            Edge e = agenda.remove();
            boolean incorporated = strategy.incorporate(e);

            if ((monitor != null) && incorporated) {
                monitor.note(e);
            }
        }
    }

    /**
     * Find the edges that span the input string
     * and have one of the desired categories.
     *
     * @param topCats the desired categories (often this will be
     * a singleton set having element "S").
     * @return the edges having the desired property
     */
    public final Set<Edge> solutions(final Set<String> topCats) {
        Set<Edge> dest = new TreeSet<Edge>();

        for (Edge e : completes.get(0)) {
            if (topCats.contains(e.getLabel()) && (e.getLeft() == 0)
                    && (e.getRight() == numWords)) {
                dest.add(e);
            }
        }

        return dest;
    }

    /**
     * Pair a complete with the partials that abut it.
     * Push the results onto the agenda
     *
     * @param complete the complete edge to pair
     * @param ps the collection of complete edges that might match
     */
    private void pairwithpartials(final Set<Edge> ps, final Edge complete) {
        for (Edge partial : ps) {
            if (partial.firstNeeded().equals(complete.getLabel())) {
                agenda.add(Edges.fundamental(partial, complete));
            }
        }
    }

    /**
     * Pair a partial with the completes that abut it.
     * Push the results onto the agenda
     *
     * @param partial the partial edge to pair
     * @param cs the collection of complete edges thar might match
     */
    private void pairwithcompletes(final Edge partial, final Set<Edge> cs) {
        for (Edge complete : cs) {
            if (partial.firstNeeded().equals(complete.getLabel())) {
                agenda.add(Edges.fundamental(partial, complete));
            }
        }
    }

    /**
     * Test driver for chart.
     * @param args not used
     */
    public static void main(final String[] args) {
        Set<String> topCats = Collections.singleton("S");
        Chart c = new Chart(args, topCats);

        for (Edge e : c.solutions(topCats)) {
            Tree t = e.firstTree();

            if (t != null) {
                System.out.println(t.asString());
            }
        }
    }

    /**
     * A bottom-up strategy for the parser.
     */
    public class BottomUpStrategy extends Strategy {

        /**
         * Create a strategy to apply to a chart.
         * @param ch the chart that the strategy works on
         */
        BottomUpStrategy(final Chart ch) {
            setMyChart(ch);
        }

        /**
         * Initialization for bottom-up strategy.
         * @param words the sentence to be tagged
         * @param topCats the allowable root categories.
         */
        @Override
        public final void initialize(
                final String[] words,
                final Set<String> topCats) {
            int i = 0;

            for (String word : words) {
                getMyChart().agenda.add(Edges.lexical(word, i));
                i++;
            }
        }

        /**
         * the bottom-up strategy predicts rule invocations here.
         *
         * @param label the label of the complete edge
         * @param position the position at which the predictions
         *  should be made.
         */
        @Override
        public final void predictFromComplete(
                final String label,
                final int position) {
            for (Rule r : rules) {
                if (r.getRhs().get(0).equals(label)) {
                    getMyChart().agenda.add(Edges.empty(r, position));
                }
            }
        }

        /**
         * The bottom-up strategy doesn't make predictions from
         * partials, but it does pair them with the corresponding
         * completes.
         *
         * @param edge the edge from which predictions should be made
         */
        @Override
        public final void predictFromPartial(final Edge edge) {
            getMyChart().pairwithcompletes(edge,
                            completes.get(edge.getRight()));
        }
    }

    /**
     * A class providing a partial implementation of parsing strategies.
     *
     */
    public abstract class Strategy {

        /**
         * the chart that the strategy owns.
         */
        private Chart myChart;

        /**
         * called to set up the parser with a string of words.
         *
         * @param words the sentence
         * @param topCats the allowed root categories
         */
        public abstract void initialize(
                final String[] words,
                final Set<String> topCats);

        /**
         * called when a complete edge is added to the chart
         * in order to do any necessary prediction of rules
         * that might apply to it.
         *
         * @param label the label of the complete edge
         * @param position the position at which the complete edge ends
         */
        public abstract void predictFromComplete(
                final String label,
                final int position);

        /**
         * called when a partial edge is added to the chart
         * in order to make any necessary predictions.
         *
         * @param e the edge from which predictions are made
         */
        public abstract void predictFromPartial(final Edge e);

        /**
         * The main driver procedure that adds edges to the chart and
         * causes the actions dictated by the strategy to fire.
         *
         * @param e an edge to incorporate
         * @return whether the chart grew
         */
        public final boolean incorporate(final Edge e) {
            TreeSet<Edge> edges;

            if (e.iscomplete()) {
                edges = (TreeSet<Edge>) getMyChart().completes.get(e.getLeft());
            } else {
                edges = (TreeSet<Edge>) getMyChart().partials.get(e.getRight());
            }

            if (edges.contains(e)) {
                Edge oldEdge = edges.tailSet(e).first();

                oldEdge.getPredecessors().addAll(e.getPredecessors());

                return false;
            } else {
                edges.add(e);

                if (e.iscomplete()) {
                    getMyChart().numCompleteEdges++;
                    predictFromComplete(e.getLabel(), e.getLeft());
                    getMyChart().pairwithpartials(partials.get(e.getLeft()), e);
                } else {
                    assert e.ispartial();
                    getMyChart().numPartialEdges++;
                    predictFromPartial(e);
                }

                return true;
            }
        }

        /**
         * @return myChart
         */
        public final Chart getMyChart() {
            return myChart;
        }

        /**
         * @param ch myChart to set
         */
        public final void setMyChart(final Chart ch) {
            this.myChart = ch;
        }
    }

    /**
     * A top down strategy for the parser.
     */
    public class TopDownStrategy extends Strategy {

        /**
         * create a strategy and associate it with a chart.
         * @param ch the chart to which the strategy applies
         */
        TopDownStrategy(final Chart ch) {
            setMyChart(ch);
        }

        @Override
        public final void initialize(
                final String[] words,
                final Set<String> topCats) {
            for (Rule r : rules) {
                if (topCats.contains(r.getLhs())) {
                    getMyChart().agenda.add(Edges.empty(r, 0));
                }
            }
        }

        /**
         * A top down strategy does not need to spawn empty edges from
         * complete edges, because all the relevant ones are generated by
         * top down prediction.
         *
         * @param label category to predict from
         * @param position position at which to predict
         */
        @Override
        public void predictFromComplete(
                final String label,
                final int position) {
            /* nothing needed here */
        }

        /**
         * The method that implements the predict and scan parts
         * of Earley's algorithm.
         * @param e the edge to predict from
         */
        @Override
        public final void predictFromPartial(final Edge e) {
            predict(e);
            scan(e);
        }

        /**
         * The scan part of Earley's algorithm.
         * @param e the edge to scan
         */
        private void scan(final Edge e) {
            int position = e.getLeft();

            if ((position < numWords)
                    && e.firstNeeded().equals(sentence[position])) {
                Edge lex = Edges.lexical(sentence[position], position);

                getMyChart().agenda.add(lex);
            }
        }

        /**
         * The predict part of Earley's algorithm.
         * @param e the edge to predict new empty edges from
         */
        private void predict(final Edge e) {

            // this is very unguided, makes many hypotheses without looking at
            // input string.
            for (Rule r : rules) {
                if (r.getLhs().equals(e.firstNeeded())) {
                    getMyChart().agenda.add(Edges.empty(r, e.getRight()));
                }
            }
        }
    }
}

