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

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;

/**
 * static factory methods for making rules.
 *
 * @author Chris Brew
 */
public final class Rules {

    /**
     * the default INTERNAL_GRAMMAR.
     */
    public static final String[] INTERNAL_GRAMMAR = {

        // Like it would be in a text file
        "S (num) -> Np(num case:subj) Vp(num) | S conj S",
        "S (num) -> Np(num case:subj) cop(num) ppart",
        "S(num) -> Np(num case:subj) cop(num) ppart passmarker Np(case:obj)",
        "Np (num case) -> det(num) Nn(num) | Np Pp | pn(num case)",
        "Np -> Np conj Np",
        "Nn(num) -> n(num) | adj n(num)",
        "Vp(num)  -> v(num tr:trans) Np(case:obj) | v(num tr:intrans)",
        "Vp(num) -> cop(num) adj",
        "Vp(num) -> Vp(num) Pp", "Pp -> prep Np(case:obj)"
    };

    /**
     * the default INTERNAL_LEXICON.
     */
    public static final String[] INTERNAL_LEXICON = {
        "a det(num:sing)", "and conj", "are cop(num:pl)", "ball n (num : sing)",
        "big adj" + "bitten ppart", "blue adj",
        "boy n(num:sing)", "boys n(num:pl)", "by passmarker | prep",
        "cage n(num:sing) | v(num:pl tr:trans)",
        "caged v(tr:trans) | ppart", "cages n(num:pl) | v(num:sing tr:trans)",
        "cafes n(num:pl)", "chris n(num:sing)",
        "computer n(num:sing)", "computers n(num:pl)",
        "detmar n(num:sing)", "enormous adj",
        "eric n(num:sing)",
        "fifty det(num:pl)", "four det(num:pl)",
        "girl n(num:sing)" + "girls n(num:pl)", "green adj",
        "he pn(num:sing case:subj)", "her pn(num:sing case:obj)",
        "him pn(num:sing case:obj)", "hit v(tr:trans) | ppart",
        "hits v(tr:trans num:sing)", "house n(num:sing)",
        "in prep", "is cop(num:sing)", "little adj",
        "mic pn(num:sing)", "mike pn(num:sing)",
        "micro n(num:sing)", "micros n(num:pl)",
        "on prep", "one n(num:sing) | pn(num:sing) | det(num:sing)",
        "ones n(num:pl)", "pdp11 n(num:sing)",
        "pdp11s n(num:pl)", "pigeon n(num:sing)", "pigeons n(num:pl)",
        "professors n(num:pl)",
        "program n(num:sing) | v(num:pl tr:trans)",
        "programmed v( tr:trans) | ppart",
        "programs n(num:pl) | v(num:sing tr:trans)",
         "punish v(num:pl tr:trans)", "punished v( tr:trans) | ppart",
        "punishes v(num:sing tr:trans)", "ran v(tr:intrans)",
        "rat n(num:sing)", "rats n(num:pl)", "red adj",
        "reinforce v (num:pl tr:trans)",
        "reinforced v ( tr:trans) | ppart", "reinforces v (num:s tr:trans)",
        "room n(num:sing)", "rooms n(num:pl)",
        "run v(tr:intrans num:pl)", "runs v(tr:intrans num:sing)",
        "scientists n(num:pl)", "she pn(num:sing case:subj)",
        "steve pn(num:sing)", "stuart pn(num:sing)",
        "suffer v(num:pl tr:intrans)", "suffered v( tr:intrans)",
        "suffers v(num:sing tr:intrans)",
        "that det(num:sing)", "the det", "them pn(num:pl case:obj)",
        "these det(num:pl)", "they pn(num:pl case:subj)",
        "those det (num:pl)", "three det(num:pl)", "two det(num:pl)",
        "undergraduates n(num:pl)",
        "universities n(num:pl)", "university n(num:sing)",
        "was cop(num:sing)", "were cop(num:pl)",
        "william n(num:sing)",
    };

    /**
     * just to keep track of parser.
     */
    private enum ParseState { INITIAL, INGRAMMAR, INLEXICON }
    /**
     * to prevent default construction.
     */
    private Rules() { }

    /**
     * add rules to a ruleset, first tidying them up.
     * @param s the string specifying the rules
     * @param rules the rules that need adding to
     */
    private static void addRules(final String s, final List<Rule> rules) {
        StringBuilder sb       = removeBalanced(s);
        int           arrowPos = sb.indexOf("->");
        String        lhs      = sb.substring(0, arrowPos).trim();
        int           start    = arrowPos + 2;
        int           end      = 0;

        while ((end = sb.indexOf("|", start)) != -1) {
            Rule r = new Rule(lhs, sb.substring(start, end).trim());

            rules.add(r);
            start = end + 1;
        }

        Rule r = new Rule(lhs, sb.substring(start, sb.length()).trim());

        rules.add(r);
    }
    /**
     * Tidy up a lexical entry before placing it in the ruleset.
     * @param s the string representing the rule
     * @param rules the list of rules we are appending to.
     */
    private static void addEntry(final String s, final List<Rule> rules) {
        StringBuilder sb       = removeBalanced(s);
        int           spacePos = sb.indexOf(" ");
        String        word     = sb.substring(0, spacePos).trim();
        int           start    = spacePos + 1;
        int           end      = 0;

        while ((end = sb.indexOf("|", start)) != -1) {
            Rule r = new Rule(sb.substring(start, end).trim(), word);

            rules.add(r);
            start = end + 1;
        }

        Rule r = new Rule(sb.substring(start, sb.length()).trim(), word);

        rules.add(r);
    }
    /**
     * Ignore the feature part of the strings.
     * @param s the string with optional feature descriptions in round
     * brackets/
     * @return s with no features in
     */
    private static StringBuilder removeBalanced(final String s) {

        // erase features (because we don't handle them)
        StringBuilder sb    = new StringBuilder(s);
        int           start = 0;

        while ((start = sb.indexOf("(")) != -1) {
            sb.delete(start, sb.indexOf(")", start) + 1);
        }

        return sb;
    }


    /**
     * read a grammar from a text file.
     *
     * @param filename the filename to read from
     * @return list of rules (conceptually a set)
     */
    public static List<Rule> grammar(final String filename) {
        try {
            BufferedReader gramin = new BufferedReader(
                    new FileReader(filename));
            String         line;
            ParseState     ps    = ParseState.INITIAL;
            List<Rule>     rules = new ArrayList<Rule>();

            while ((line = gramin.readLine()) != null) {
                if (line.equals("grammar")) {
                    ps = ParseState.INGRAMMAR;
                } else if (line.equals("thatsall")) {
                    ps = ParseState.INITIAL;
                } else if (line.equals("lexicon")) {
                    ps = ParseState.INLEXICON;
                } else if (ps == ParseState.INLEXICON) {
                    addEntry(line, rules);
                } else if (ps == ParseState.INGRAMMAR) {
                    addRules(line, rules);
                }
            }

            gramin.close();

            return rules;
        } catch (IOException e) {
            return null;
        }
    }
    /**
     * Get the left hand sides of a rule set as a set of strings.
     * @param rs the rules to get the lhses of
     * @return set of left hand side strings
     */
    private static Set<String> leftHandSides(final List<Rule> rs) {
        Set<String> xs = new TreeSet<String>();

        for (Rule r : rs) {
            xs.add(r.getLhs());
        }

        return xs;
    }
    /**
     * Make a ruleset in form of a map.
     * @param rs the input ruleset
     * @return a map from lhses to lists of rules with that lhs
     */
    private static Map<String, List<Rule>> rulesByLhs(final List<Rule> rs) {
        Set<String>                 lhss = leftHandSides(rs);
        TreeMap<String, List<Rule>> tm   = new TreeMap<String, List<Rule>>();

        for (String lhs : lhss) {
            tm.put(lhs, new ArrayList<Rule>());
        }

        for (Rule r : rs) {
            tm.get(r.getLhs()).add(r);
        }

        return tm;
    }

    /**
     * A default INTERNAL_GRAMMAR read from strings found in this file.
     * @return a set of rules
     */
    public static List<Rule> english() {
        List<Rule> rules = new ArrayList<Rule>();

        for (String r : INTERNAL_GRAMMAR) {
            addRules(r, rules);
        }

        for (String w : INTERNAL_LEXICON) {
            addEntry(w, rules);
        }

        return rules;
    }
}
