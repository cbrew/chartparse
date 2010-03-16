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
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

/**
 * The data structure for a syntax tree.
 *
 * @author Chris Brew
 */
public class Tree {

    /**
     * empty list.
     */
    public static final List<Tree> EMPTY = Collections.emptyList();

    /**
     * The children.
     */
    private final List<Tree> children;

    /**
     * The mother node.
     */
    private final String parent;

    /**
     * constructor for leaf.
     * @param p the leaf label
     */
    public Tree(final String p) {
        this(p, EMPTY);
    }

    /**
     * constructor for internal node.
     * @param p the mother node label
     * @param cs the children
     */
    public Tree(final String p, final List<Tree> cs) {
        parent   = p;
        children = cs;
    }

    /**
     * convenience constructor to allow <code>Tree [] cs</code>.
     * @param p label for mother node
     * @param cs children
     */
    public Tree(final String p, final Tree[] cs) {
        this(p, Arrays.asList(cs));
    }

    /**
     * constructor for combining two trees.
     * @param p partial edge
     * @param c complete edge
     * @return resulting tree
     */
    public static Tree adjoin(final Tree p, final Tree c) {
        List<Tree> newchildren = new ArrayList<Tree>(p.children);

        newchildren.add(c);

        Tree tr = new Tree(p.parent, newchildren);

        return tr;
    }

    /**
     * create string representation of tree.
     * This one does surrounding brackets.
     * @param s the <code>the StringBuilder</code> we are writing to.
     * @param tab the number of spaces to prefix line with.
     */
    private void treestring2(final StringBuilder s, final int tab) {
        s.append('\n');

        for (int i = 0; i < tab; i++) {
            s.append(' ');
        }

        s.append('(');

        if ((children.size() == 1) && (children.get(0).children.size() == 0)) {
            s.append(parent + " " + children.get(0).parent);
        } else {
            s.append(parent);

            for (Tree child : children) {
                child.treestring2(s, tab + 1);
            }
        }

        s.append(')');
    }

    /**
     * create string representation of tree.
     *
     * This one doesn't do brackets.
     *
     * @param s the <code>the StringBuilder</code> we are writing to.
     * @param tab the number of spaces to prefix line with.
     */
    @SuppressWarnings("unused")
    private void treestring(final StringBuilder s, final int tab) {
        for (int i = 0; i < tab; i++) {
            s.append(' ');
        }

        if ((children.size() == 1) && (children.get(0).children.size() == 0)) {
            s.append(parent + " " + children.get(0).parent + "\n");
        } else {
            s.append(parent);
            s.append('\n');

            for (Tree child : children) {
                child.treestring(s, tab + 1);
            }
        }
    }

    /**
     * The string representation of a tree.
     * @return the string.
     */
    public final String asString() {
        StringBuilder s = new StringBuilder();

        treestring2(s, 0);

        return s.toString();
    }

    /**
     * Test driver for printing trees.
     * @param args unused
     */
    public static void main(final String[] args) {
        Tree[] subtrees = {new Tree("np"), new Tree("vp") };
        Tree   t        = new Tree("s", subtrees);

        System.out.println(t.asString());
    }

    /**
     * @return the children
     */
    public final List<Tree> getChildren() {
        return children;
    }

    /**
     * @return the parent
     */
    public final String getParent() {
        return parent;
    }
}
