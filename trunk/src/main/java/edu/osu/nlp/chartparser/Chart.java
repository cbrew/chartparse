/**
 * Copyright (C) 2010 cbrew <cbrew@acm.org>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *         http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
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
    public final ArrayList<Set<Edge>> partials;
    /**
     * the grammar used.
     */
    public final List<Rule> rules;
    /**
     * the sentence being parsed.
     */
    public String[] sentence;

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
    public final void pairwithpartials(final Set<Edge> ps, final Edge complete)
    {
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
     public final void pairwithcompletes(final Edge partial, final Set<Edge> cs)
    {
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
     * accessor for agenda.
     * @return the agenda
     */
    public final Queue<Edge> getAgenda() {
        return agenda;
    }

    /**
     * accessor for completes.
     * @return the completes
     */
    List<Set<Edge>> getCompletes() {
        return completes;
    }

    void incrementCompletes() {
        numCompleteEdges++;
    }

    void incrementPartials(){
        numPartialEdges++;
    }

    final int getNumWords() {
        return numWords;
    }
}

