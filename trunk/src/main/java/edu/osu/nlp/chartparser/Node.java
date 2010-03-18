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

/**
 * Horizontally placed tree.
 * @author cbrew
 */

final class Node {
    /**
     * Private constructor for making nodes.
     * @param myTree the tree
     * @param myHpos the relative horizontal position of the tree
     */
    private Node(final Tree myTree, final double myHpos) {
        tree = myTree;
        hpos = myHpos;
    }

    /**
     * The relative horizontal position of the current tree.
     */
    private final double hpos;

    /**
     * The tree being laid out here.
     */
    private final Tree tree;

    /**
     * Create a horizontally shifted version of a node.
     * @param e  the original extent
     * @param shift how much to shift
     * @return the new extent
     */
    public static Node move(final Node e, final double shift) {
        return new Node(e.getTree(), e.getHpos() + shift);
    }

    /**
     * Create a node positioned at the leftmost edge of its space.
     * @param tr the tree on which to build.
     * @return the new extent
     */

    public static Node atLeft(final Tree tr) {
        return new Node(tr, 0.0);
    }

    /**
     * @return the hpos
     */
    public double getHpos() {
        return hpos;
    }

    /**
     * @return the tree
     */
    public Tree getTree() {
        return tree;
    }
}
