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

import java.lang.Comparable;

/**
 * The data structure that enables trace back
 * by recording the partners in an application
 * of the fundamental rule.
 *
 * @author Chris Brew
 * @version 0.5
 */


public class TraceEntry implements Comparable<TraceEntry> {
    public Edge partial; 
    public Edge complete;

    public TraceEntry(Edge p,Edge c) {
	partial = p; 
	complete = c; 
    }
    
    /**
     * compare two edges for ordering
     */

    public int compareTo(TraceEntry other){
    	int x = partial.compareTo(other.partial);
    	if(x != 0)
    		return x;
    	else
    		return complete.compareTo(other.complete);
	
    }

};