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


import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Random;

/**
 * The OSU CSE 732 generator.
 *
 * @author Chris Brew
 */
public class Generator {

    /**
     * hard-wired grammar.
     */
    private static final Collection<Rule> RULES = Rules.grammar("grammar.txt");
    /**
     * random number generator.
     */
    private final Random rnd;

    /**
     * Create a generator with Java's default seed.
     */
    public Generator() {
      rnd = new Random();
    }
    /**
     * Create a generator.
     * @param seed if <code>seed != 0</code> use it, else whatever Java gives
     */
     public Generator(final int seed) {
             rnd = new Random(seed);
    }

    /**
     * randomly generate the next tree based on a given lhs.
     *
     *
     * @param lhs to generate from
     * @return randomly generated tree
     */
    public final Tree nextTree(final String lhs) {

        // look up relevant rules for lhs.
        // with a different organization of the grammar this
        // would be a hash table lookup, and maybe a bit faster
        ArrayList<Rule> relevant = new ArrayList<Rule>();

        for (Rule r : RULES) {
            if (r.getLhs().equals(lhs)) {
                relevant.add(r);
            }
        }

        if (relevant.size() == 0) {

            // we have a leaf
            return new Tree(lhs);
        } else {
            // we have an internal node whose subtrees must be generated
            ArrayList<Tree> subtrees = new ArrayList<Tree>();
            Rule            r        = relevant.get(
                    rnd.nextInt(relevant.size()));

            for (String clhs : r.getRhs()) {
                subtrees.add(nextTree(clhs));
            }

            return new Tree(lhs, subtrees);
        }
    }

    /**
     *
     * @param args <code>args[0]</code> integer saying how many sentences
     * @throws IOException if output routines fail
     */
    public static void main(final String[] args) throws IOException {
        // always use same seed, for ease of debugging
        final int defaultSeed = 0x123456;
        Generator g = new Generator(defaultSeed);
        Integer   n = Integer.parseInt(args[0]);

        for (int i = 0; i < n; i++) {
            System.out.println(g.nextTree("S").asString());
        }
    }
}

