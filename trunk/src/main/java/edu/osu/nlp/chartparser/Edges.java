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


/**
 * Static factory methods for making edges. 
 *
 * @author Chris Brew
 * @version 0.5
 */

public class Edges {
    /**
     * Create a length 1 lexical edge for a word
     *
     * @param word the word 
     * @param start the start position of the lexical edge
     */
    public static Edge lexical(String word,int start) { 
    	Edge e = new Edge(word,start); 

    	return e;	
    }
    /**
     * Create an empty edge from a rule
     *
     * @param lhs the rule's left hand side
     * @param position the position of the empty edge 
     * @param rhs the rule's right hand side
     */
    public static Edge empty(Rule r,int position) { 
    	Edge e = new Edge(r.lhs,position,r.rhs);

    	return e;
    }

    /**
     * Create an edge via the fundamental rule
     *
     * @param partial the partial edge
     * @param complete the complete edge
     */

    public static Edge fundamental(Edge partial,Edge complete) { 
    	Edge e = new Edge(partial,complete);

    	return e;
    }
};
 