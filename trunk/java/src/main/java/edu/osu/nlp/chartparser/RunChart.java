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

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintStream;
import java.util.Arrays;
import java.util.Collections;
import java.util.ResourceBundle;
import java.util.Set;

/**
 * Driver for the OSU CSE 732 chart parser.
 *
 * @author Chris Brew
 */
public final class RunChart {
    /**
     * to suppress default constructor.
     */
    private RunChart() { }

    /**
     * turn tree printing on or off.
     */

    private static boolean     printTrees;

    /**
     * possibly print trees to a stream.
     */
    private static PrintStream treesOut;

    /**
     * run parser.
     * @param words the sentence to parse
     * @throws IOException If an input or output exception occurred
     */
    private static void parse(final String[] words) throws IOException {
        Set<String> topCats = Collections.singleton("S");
        Chart       c       = new Chart(words, topCats);

        treesOut.println(Arrays.asList(words));

        for (Edge e : c.solutions(topCats)) {
            int treeNum = 0;

            if (printTrees) {
                for (Tree t : e.allTrees()) {
                    treesOut.println("Tree: " + treeNum);
                    treeNum++;
                    treesOut.println(t.asString());
                }
            }
        }
    }

    /**
     * Runs the chart parser on a file of sentences.
     * @param args  ignored
     * @throws IOException If an input or output exception occurred.
     */
    public static void main(final String[] args) throws IOException {
         ResourceBundle bundle = ResourceBundle.getBundle("Chart");
        String sentenceFile = bundle.getString("parser.sentences");
        String line;

        treesOut = System.out;

        BufferedReader in     = new BufferedReader(
                new FileReader(sentenceFile));
       

        printTrees = bundle.getString("parser.printTrees").equals("true");

        while ((line = in.readLine()) != null) {
            String[] words = line.trim().split(" +");

            parse(words);
        }
    }
}
