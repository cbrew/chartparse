/*
 * OsuChart v. 0.5
 * Copyright (C) 2009 Chris Brew
 *
 * This file is part of OsuChart.
 *
 * OsuChart is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * OsuChart is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with OsuChart.  If not, see <http://www.gnu.org/licenses/>.
 */

package edu.osu.nlp.chartparser;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.Set;
import java.util.TreeSet;
import java.util.TreeMap;

/**
 * static factory methods for making rules.
 * Assignment 2.2 requires you to supersede this with a better design
 *
 * @author Chris Brew
 * @version 0.5
 **/

public class Rules {
	
	
	private static final Random rnd = new Random(0x123456);
	
    /**
     * the default grammar
     */
    public static final String [] grammar = { 
	// Like it would be in a text file
	"S (num) -> Np(num case:subj) Vp(num) | S conj S",
	"S (num) -> Np(num case:subj) cop(num) ppart",
	"S(num) -> Np(num case:subj) cop(num) ppart passmarker Np(case:obj)",
	"Np (num case) -> det(num) Nn(num) | Np Pp | pn(num case)",
	"Np -> Np conj Np",
	"Nn(num) -> n(num) | adj n(num)",
	"Vp(num)  -> v(num tr:trans) Np(case:obj) | v(num tr:intrans) | cop(num) adj",
	"Vp(num) -> Vp(num) Pp",
        "Pp -> prep Np(case:obj)"};

    /**
     * the default lexicon
     */
    public static final String [] lexicon = {
	"a det(num:sing)",
	"and conj",
	"are cop(num:pl)",
	"ball n (num : sing)",
	"big adj"+
	"bitten ppart",
	"blue adj",
	"boy n(num:sing)",
	"boys n(num:pl)",
	"by passmarker | prep",
	"cage n(num:sing) | v(num:pl tr:trans)",
	"caged v(tr:trans) | ppart",
	"cages n(num:pl) | v(num:sing tr:trans)",
	"cafes n(num:pl)",
	"chris n(num:sing)",
	"computer n(num:sing)",
	"computers n(num:pl)",
	"enormous adj",
	"fifty det(num:pl)",
	"four det(num:pl)",
	"girl n(num:sing)"  +
	"girls n(num:pl)",
	"green adj",
	"he pn(num:sing case:subj)",
	"her pn(num:sing case:obj)",
	"him pn(num:sing case:obj)",
	"hit v(tr:trans) | ppart",
	"hits v(tr:trans num:sing)",
	"house n(num:sing)",
	"in prep",
	"is cop(num:sing)",
	"little adj",
	"mic pn(num:sing)",
	"micro n(num:sing)",
	"micros n(num:pl)",
	"on prep",
	"one n(num:sing) | pn(num:sing) | det(num:sing)",
	"ones n(num:pl)",
	"pdp11 n(num:sing)",
	"pdp11s n(num:pl)",
	"pigeon n(num:sing)",
	"pigeons n(num:pl)",
	"professors n(num:pl)",
	"program n(num:sing) | v(num:pl tr:trans)",
	"programmed v( tr:trans) | ppart",
	"programs n(num:pl) | v(num:sing tr:trans)",
	"punish v(num:pl tr:trans)",
	"punished v( tr:trans) | ppart",
	"punishes v(num:sing tr:trans)",
	"ran v(tr:intrans)",
	"rat n(num:sing)",
	"rats n(num:pl)",
	"red adj",
	"reinforce v (num:pl tr:trans)",
	"reinforced v ( tr:trans) | ppart",
	"reinforces v (num:s tr:trans)",
	"room n(num:sing)",
	"rooms n(num:pl)",
	"run v(tr:intrans num:pl)",
	"runs v(tr:intrans num:sing)",
	"scientists n(num:pl)",
	"she pn(num:sing case:subj)",
	"steve pn(num:sing)",
	"stuart pn(num:sing)",
	"suffer v(num:pl tr:intrans)",
	"suffered v( tr:intrans)",
	"suffers v(num:sing tr:intrans)",
	"that det(num:sing)",
	"the det",
	"them pn(num:pl case:obj)",
	"these det(num:pl)",
	"they pn(num:pl case:subj)",
	"those det (num:pl)",
	"three det(num:pl)",
	"two det(num:pl)",
	"undergraduates n(num:pl)",
	"universities n(num:pl)",
	"university n(num:sing)",
	"was cop(num:sing)", 
	"were cop(num:pl)"};




    private Rules() {} // to prevent default constructor
    


    private static void addRules(String s,List<Rule> rules) {
	StringBuilder sb = removeBalanced(s);
	int arrowPos = sb.indexOf("->");
	String lhs = sb.substring(0,arrowPos).trim();
    
	int start = arrowPos+2;
	int end = 0;
	


	while((end = sb.indexOf("|",start)) != -1) {
	    Rule r = new Rule(lhs,sb.substring(start,end).trim());
	    rules.add(r);
	    start = end+1;
	}
	Rule r = new Rule(lhs,sb.substring(start,sb.length()).trim());
	rules.add(r);

    }

    private static void addEntry(String s,List<Rule> rules) {
	StringBuilder sb = removeBalanced(s);

	int spacePos = sb.indexOf(" ");
	String word = sb.substring(0,spacePos).trim();
	int start = spacePos + 1;
	int end = 0;
	
	while((end = sb.indexOf("|",start)) != -1) {
	    Rule r = new Rule(sb.substring(start,end).trim(),word);
	    rules.add(r);
	    start = end+1;
	}
	Rule r = new Rule(sb.substring(start,sb.length()).trim(),word);
	rules.add(r);
	
	
    }

    private static StringBuilder removeBalanced(String s) {
	// erase features (because we don't handle them)
	StringBuilder sb = new StringBuilder(s);
	int start = 0;
	
	while((start = sb.indexOf("(")) != -1) {
	    sb.delete(start,sb.indexOf(")",start)+1);
	}
	
	return sb;
    }

    private enum ParseState {INITIAL,INGRAMMAR,INLEXICON};
    
    /**
     * read a grammar from a textfile
     *
     * @param filename the filename to read from
     */
    public static List<Rule> grammar(String filename)  {
	try {
	    BufferedReader gramin = new BufferedReader(new FileReader(filename));
	    String line;
	    ParseState ps = ParseState.INITIAL;

	    List<Rule> rules = new ArrayList<Rule>();
	       

	    while((line = gramin.readLine()) != null) {
		if(line.equals("grammar")){
		    ps = ParseState.INGRAMMAR;
		
		}else if(line.equals("thatsall")) {
		    ps = ParseState.INITIAL;
		} else if(line.equals("lexicon")){
		    ps = ParseState.INLEXICON;
		} else if(ps == ParseState.INLEXICON) {
		    addEntry(line,rules);
		} else if (ps == ParseState.INGRAMMAR) {
		    addRules(line,rules);
		}
	    }
	    
	    gramin.close();
	    
	    return rules;
	} catch (IOException e) {
	    return null;
	}
    }

    
    private static Set<String> leftHandSides(List<Rule> rs){
    	Set<String> xs = new TreeSet<String>();
    	
    	for(Rule r: rs){
    		xs.add(r.lhs);
    	}
    	return xs;
    }
    
    
    private static Map<String,List<Rule>> rulesByLhs(List<Rule> rs) {
    	Set<String> lhss = leftHandSides(rs);
    	TreeMap<String,List<Rule>> tm = new TreeMap<String,List<Rule>>();
    	for(String lhs:lhss)
    		tm.put(lhs, new ArrayList<Rule>());
    	for(Rule r: rs){
    		tm.get(r.lhs).add(r);
    	}
    	
    	return tm;
    	
    }
    
    
    /**
     * A default grammar read from strings found in this file
     */
    public static List<Rule> english() { 
	List<Rule> rules = new ArrayList<Rule>();
	for(String r: grammar){
	    addRules(r,rules);
	}
	for(String w: lexicon) {
	    
	    addEntry(w,rules);
	}
	
	
	
	return rules;
	
    }
}
