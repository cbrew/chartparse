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

import java.util.Set;
import java.util.TreeSet;

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
     * The chart that this strategy has.
     * @param myChart
     */
    public Strategy(Chart myChart) {
        this.myChart = myChart;
    }

    /**
     * called to set up the parser with a string of words.
     *
     * @param words the sentence
     * @param topCats the allowed root categories
     */
    public abstract void initialize(final String[] words, final Set<String> topCats);

    /**
     * called when a complete edge is added to the chart
     * in order to do any necessary prediction of rules
     * that might apply to it.
     *
     * @param label the label of the complete edge
     * @param position the position at which the complete edge ends
     */
    public abstract void predictFromComplete(final String label, final int position);

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
            edges = (TreeSet<Edge>) myChart.completes.get(e.getLeft());
        } else {
            edges = (TreeSet<Edge>) myChart.partials.get(e.getRight());
        }
        if (edges.contains(e)) {
            Edge oldEdge = edges.tailSet(e).first();
            oldEdge.getPredecessors().addAll(e.getPredecessors());
            return false;
        } else {
            edges.add(e);
            if (e.iscomplete()) {
                myChart.numCompleteEdges++;
                predictFromComplete(e.getLabel(), e.getLeft());
                myChart.pairwithpartials(myChart.partials.get(e.getLeft()), e);
            } else {
                assert e.ispartial();
                myChart.numPartialEdges++;
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
