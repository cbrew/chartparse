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

/**
 * The data structure that enables trace back
 * by recording the partners in an application
 * of the fundamental rule.
 *
 * @author Chris Brew
 */
public class TraceEntry implements Comparable<TraceEntry> {

    /**
     * A complete edge ancestor of current edge.
     */
    private Edge complete;
    /**
     * complete edge ancestor of current edge.
     */
    private Edge partial;

    /**
     * Create a trace entry from matching partial and complete edges.
     * @param p the partial edge
     * @param c the complete edge
     */
    public TraceEntry(final Edge p, final Edge c) {
        partial  = p;
        complete = c;
    }

    /**
     * compare two edges for ordering.
     * @param other the edge to compare with the current one
     * @return -1, 0, +1 depending on ordering
     */
    @Override
    public final int compareTo(final TraceEntry other) {
        int x = partial.compareTo(other.partial);

        if (x != 0) {
            return x;
        } else {
            return complete.compareTo(other.complete);
        }
    }

    /**
     * @return the complete
     */
    public final Edge getComplete() {
        return complete;
    }

    /**
     * @param c the complete to set
     */
    public final void setComplete(final Edge c) {
        this.complete = c;
    }

    /**
     * @return the partial
     */
    public final Edge getPartial() {
        return partial;
    }

    /**
     * @param p the partial to set
     */
    public final void setPartial(final Edge p) {
        this.partial = p;
    }
}

