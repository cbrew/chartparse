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

import java.util.ArrayList;
import java.util.Collections;
import java.util.Iterator;
import java.util.List;
import java.util.SortedSet;
import java.util.TreeSet;

/**
 * The data structure that stores hypotheses about spans of the input string.
 *
 * @author Chris Brew
 */
public class Edge implements Comparable<Edge> {

    /**
     * We create a singleton static empty list as a convenience.
     */
    private static final List<String> EMPTY = Collections.emptyList();
    /**
     * an edge has a myLabel that is a string.
     */
    private final String label;
    /**
     * an edge has an index for its myLeft end.
     */
    private final int left;
    /**
     * list of strings still needed.
     */
    private final List<String> needed;
    /**
     * information about way(s) this edge is licensed.
     */
    private final SortedSet<TraceEntry> predecessors;
    /**
     * index for right end.
     */
    private final int right;

    /**
     * create an edge via the fundamental rule.
     * @param partial a partial edge seeking something
     * @param complete a complete edge providing what partial needs
     */
    public Edge(final Edge partial, final Edge complete) {

        // fundamental rule
        this(partial.getLabel(), partial.getLeft(), complete.getRight(),
                partial.needed.subList(1, partial.needed.size()));

        // track predecessors
        predecessors.add(new TraceEntry(partial, complete));
        assert (partial.needed.get(0).equals(complete.getLabel()));
    }

    /**
     * create a lexical edge from a word.
     * @param word the string representing the word
     * @param start the starting position
     */
    public Edge(final String word, final int start) {

        // lexical edge
        this(word, start, start + 1, EMPTY);
    }

    /**
     * Create an empty (predictive) edge from rule and position.
     * @param lhs   the myLabel
     * @param position the position
     * @param rhs the right hand side of the rule
     */
    public Edge(final String lhs, final int position, final List<String> rhs) {

        // EMPTY edge
        this(lhs, position, position, rhs);
    }

    /**
     * Internal constructor that the others delegate to.
     * @param myLabel the label
     * @param myLeft   the left indexs
     * @param myRight  the right index
     * @param myNeeded the list of things needed
     */
    private Edge(final String myLabel,
                final int myLeft,
                final int myRight,
                final List<String> myNeeded) {

        // the public constructors delegate to this one
        this.label = myLabel;
        this.left = myLeft;
        this.right = myRight;
        this.needed = myNeeded;
        predecessors = new TreeSet<TraceEntry>();
    }

    /**
     * @return the myLabel
     */
    public final String getLabel() {
        return label;
    }

    /**
     * @return the leftTree
     */
    public final int getLeft() {
        return left;
    }

    /**
     * @return the rightTree
     */
    public final int getRight() {
        return right;
    }

    /**
     *
     * @return the next category needed by the current edge
     */
    public final String firstNeeded() {
        return needed.get(0);
    }

    /**
     *
     * @return all categories needed by the current edge
     */
    public final List<String> getNeeded() {
        return needed;
    }

    /**
     * Test whether an edge is finished.
     * @return true if edge is complete
     */
    public final boolean iscomplete() {
        return needed.isEmpty();
    }

    /**
     * Test whether an edge still lacks anything.
     * @return true if edge is partial
     */
    public final boolean ispartial() {
        return !iscomplete();
    }

    /**
     * Return the first Tree corresponding to an edge.
     *
     * @return a tree
     */
    public final Tree firstTree() {

        // generate the first tree.
        // What "first" means depends on the function that orders
        // TraceEntries.
        if (predecessors.size() > 0) {
            TraceEntry trace = predecessors.first();
            Tree leftTree = trace.getPartial().firstTree();
            Tree rightTree = trace.getComplete().firstTree();
            List<Tree> newchildren =
                    new ArrayList<Tree>(leftTree.getChildren());

            newchildren.add(rightTree);

            return Tree.adjoin(leftTree, rightTree);
        } else {
            return new Tree(getLabel());
        }
    }

    /**
     * Count the trees under an edge.
     *
     * @return Number of trees under that edge
     */
    public final int countTrees() {

        // Assignment 2.6
        // Count the trees that are rooted at edge.
        if (predecessors.size() > 0) {
            int count = 0;

            for (TraceEntry trace : predecessors) {
                int lcount = trace.getPartial().countTrees();
                int rcount = trace.getComplete().countTrees();

                count += (lcount * rcount);
            }

            return count;
        } else {
            return 1;
        }
    }

    /**
     * Get a specified tree from this edge. Note that this is
     * NOT suitable for use when the trees need to be returned
     * in best-first order.
     *
     * @param index the index of the tree to be returned.
     * Should be less than the number of trees available.
     * @return the required tree
     */
    public final Tree getTree(final int index) {
        assert (countTrees() >= index);

        if (predecessors.size() > 0) {
            int skipped = 0;

            for (TraceEntry trace : predecessors) {
                int lcount = trace.getPartial().countTrees();
                int rcount = trace.getComplete().countTrees();
                int treesInBranch = (lcount * rcount);
                int localIndex = index - skipped;

                if (localIndex < treesInBranch) {

                    // the tree we seek is in this branch ...
                    Tree leftTree =
                            trace.getPartial().getTree(localIndex / rcount);
                    Tree rightTree =
                            trace.getComplete().getTree(localIndex % rcount);

                    return Tree.adjoin(leftTree, rightTree);
                }

                skipped += treesInBranch;
            }

            return null;
        } else {
            return new Tree(label);
        }
    }

    /**
     * Generate all trees from the current edge.
     *
     * @return Iterable suitable for use with Java's new style for loop
     */
    public final Iterable<Tree> allTrees() {

        return new AllTreesIterable(this);
    }

    /**
     * Equality tester that ignores the predecessor field.
     *
     * @param o the object against which this should be compared for equality
     * @return whether this = o
     */
    @Override
    public final boolean equals(final Object o) {
        if (!(o instanceof Edge)) {
            return false;
        }

        Edge other = (Edge) o;

        return ((getLeft() == other.getLeft())
                && (getRight() == other.getRight())
                && getLabel().equals(other.getLabel())
                && needed.equals(other.needed));
    }

    /**
     * The hash code does not compare the predecessors field.
     * @return an integer hash code
     */
    @Override
    public final int hashCode() {
        final int hashMagicOne = 5;
        final int hashMagicTwo = 83;

        int hash = hashMagicOne;

        if (this.label != null) {
                    hash += hashMagicTwo  + this.label.hashCode();
          } else {
               hash += hashMagicTwo;
         }
        hash =  hashMagicTwo * hash + this.left;
        hash =  hashMagicTwo * hash + this.right;

        if (this.needed != null) {
                    hash += hashMagicTwo  + this.needed.hashCode();
          } else {
               hash += hashMagicTwo;
         }

        return hash;
    }

    /**
     * Comparison method that ignores the predecessor field, as needed for sets.
     *
     * @param other the Edge against which this should be compared for equality
     * @return result of comparison btwn <code>this</code> and
     * <code>other</code>
     */
    @Override
    public final int compareTo(final Edge other) {
        int x = getLeft() - other.getLeft();

        if (x != 0) {
            return x;
        }

        x = getRight() - other.getRight();

        if (x != 0) {
            return x;
        }

        x = getLabel().compareTo(other.getLabel());

        if (x != 0) {
            return x;
        }

        x = needed.size() - other.needed.size();

        if (x != 0) {
            return x;
        }

        for (int i = 0; i < needed.size(); i++) {
            x = needed.get(i).compareTo(other.needed.get(i));

            if (x != 0) {
                return x;
            }
        }

        return 0;
    }

    /**
     * @return humsn readable string representation of edge
     */
    public final String asString() {
        if (iscomplete()) {
            return label + ":" + left + "-" + right;
        } else {
            return label + ":" + left + "-" + right + "/" + needed;
        }
    }

    /**
     * @return the predecessors
     */
    public final SortedSet<TraceEntry> getPredecessors() {
        return predecessors;
    }
    /**
     * Produce an iterator that unpacks the chart.
     */
    private class AllTreesIterable implements Iterable<Tree> {

        /**
         * the edge we are iterating over.
         */
        private final Edge edge;

        /**
         * create an iterable over treesfrom an edge.
         * @param e the edge
         */
        public AllTreesIterable(final Edge e) {
            edge = e;
        }

        @Override
        public Iterator<Tree> iterator() {
            return new AllTreesIterator();
        }

        /**
         * @return the edge
         */
        public Edge getEdge() {
            return edge;
        }
        /**
         * Iterate over the trees by first counting them then indexing
         * them.
         */
        private class AllTreesIterator implements Iterator<Tree> {
            /**
             * count the trees first.
             */
            private int treesRemaining = getEdge().countTrees();

            @Override
            public boolean hasNext() {
                return treesRemaining > 0;
            }

            @Override
            public Tree next() {
                assert (treesRemaining > 0);
                treesRemaining--;

                return getEdge().getTree(treesRemaining);
            }

            @Override
            public void remove() {
            }
        }
    };
};


