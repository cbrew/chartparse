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
 * class for laying out trees in 2-D.
 *
 * This is an implementation of Andrew J. Kennedy's <i>Functional Pearl</i>:
 * "Drawing Trees", J. Functional Programming, 6(3) 527-534, May 1996
 * @author Chris Brew
 */
public final class TreeLayout {
    /**
     * Create a representation of the tree layout.
     * 1) Two nodes at the same level should be at least HGAP apart.
     * @param tr a tree to lay out
     */
    private TreeLayout(final Tree tr) { }
    /**
     * The number of layout units apart nodes at the same level should be.
     */
   static final int HGAP = 1;
    /**
     * Create a layout for a tree.
     * @param tr the tree to lay out
     * @return a laid out tree
     */
    static TreeLayout layout(final Tree tr) {
        return new TreeLayout(tr);
    }
}
