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
 