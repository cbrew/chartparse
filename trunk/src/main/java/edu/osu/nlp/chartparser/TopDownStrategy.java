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

/**
 * A top down strategy for the parser.
 */
public class TopDownStrategy extends Strategy {


    TopDownStrategy(final Chart ch) {
        super(ch);
    }

    @Override
    public final void initialize(final String[] words, final Set<String> topCats) {
        for (Rule r : getMyChart().rules) {
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
    public void predictFromComplete(final String label, final int position) {
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
        if (( position < getMyChart().numWords ) && e.firstNeeded().equals(getMyChart().sentence[position])) {
            Edge lex = Edges.lexical(getMyChart().sentence[position], position);
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
        for (Rule r : getMyChart().rules) {
            if (r.getLhs().equals(e.firstNeeded())) {
                getMyChart().agenda.add(Edges.empty(r, e.getRight()));
            }
        }
    }
}