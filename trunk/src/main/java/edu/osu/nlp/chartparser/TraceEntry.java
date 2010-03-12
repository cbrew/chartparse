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