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
import java.util.List;
import java.lang.Comparable;
import java.util.Collections;
import java.util.SortedSet;
import java.util.TreeSet;
import java.lang.Iterable;
import java.util.Iterator;

/**
 * The data structure that stores hypotheses about spans of the input string. 
 *
 * @author Chris Brew
 * @version 0.5
 */
public class Edge implements Comparable<Edge>  {
    private final String label;
    private final int left;
    private final int right;
    private final List<String> needed;
    private final SortedSet<TraceEntry> predecessors;
    
    private static final List<String> empty = Collections.emptyList();
  

    private Edge(String label,int left,int right,List<String> needed) {
    	// the public constructors delegate to this one
    	this.label = label;
    	this.left = left;
    	this.right = right;
    	this.needed = needed;
    	predecessors = new TreeSet<TraceEntry>();
    }
    

    public Edge(Edge partial,Edge complete) {
	// fundamental rule
	this(partial.getLabel(),
	     partial.getLeft(),
	     complete.getRight(),
	     partial.needed.subList(1,partial.needed.size()));
	// track predecessors
	predecessors.add(new TraceEntry(partial,complete));

	assert(partial.needed.get(0).equals(complete.getLabel()));

    }

    public Edge(String word,int start) {
	// lexical edge
	this(word,start,start+1,empty);
    }

    public Edge(String lhs,int position,List<String> rhs) {
	// empty edge
	this(lhs,position,position,rhs);
    }

    /**
     * @return the label
     */
    public String getLabel() {
	return label;
    }

    /**
     * @return the left
     */
    public int getLeft() {
	return left;
    }

    /**
     * @return the right
     */
    public int getRight() {
	return right;
    }

	

    public String firstNeeded() {
	return needed.get(0);
    }


    public List<String> getNeeded() {
	return needed;
    }
    

	/**
	 * Test whether an edge still lacks anything	
	 * @return whether the edge is complete or not
	 */
	public boolean iscomplete() {
		return needed.isEmpty();
    }

	
	/**
	 * Test whether an edge still lacks anything
	 * @return whether the edge is complete or not
	 */
    public boolean ispartial() {
    	return ! iscomplete();
    }


    /**
     * Return the first Tree corresponding to an edge
     *
     * @return a tree
     */

    public Tree firstTree() {
	// generate the first tree.
	// What "first" means depends on the function that orders
	// TraceEntries. 

    	if(predecessors.size() > 0) {
    		TraceEntry trace = predecessors.first();
    		Tree left = trace.partial.firstTree();
    		Tree right = trace.complete.firstTree();
    		List<Tree> newchildren = new ArrayList<Tree>(left.children);
    		newchildren.add(right);
    		return Tree.adjoin(left,right);
    	} else {
    		return new Tree(getLabel());
			}
    	}
    
    
    
    /**
     * Count the trees under an edge
     *
     * @return Number of trees under that edge
     */

    public int countTrees() {
	//  Assignment 2.6
	//  Count the trees that are rooted at edge. Do not
	//  do this by enumerating these trees


	if(predecessors.size() > 0) {
	    int count = 0;
	    for(TraceEntry trace: predecessors) {
		int lcount = trace.partial.countTrees();
		int rcount = trace.complete.countTrees();
		count += (lcount*rcount);
	    }
	    return count;
	} else {
	    return 1;
	}
    }


    /**
     * Get a specified tree from this edge. Note that this is 
     * NOT suitable for use when the trees need to be returned
     * in best-first order. 
     * 
     * @param index the index of the tree to be returned. 
     * Should be less than the number of trees available.
     */

    public Tree getTree(int index) {

	assert(countTrees() >= index); 

	if(predecessors.size() > 0) {
	    int skipped = 0;
	    for(TraceEntry trace: predecessors) {

		int lcount = trace.partial.countTrees();
		int rcount = trace.complete.countTrees();
		int treesInBranch = (lcount*rcount);  
		
		int localIndex = index - skipped;
		if(localIndex < treesInBranch) {
		    // the tree we seek is in this branch ...
		    Tree leftTree = trace.partial.getTree(localIndex  / rcount);
		    Tree rightTree = trace.complete.getTree(localIndex % rcount);
		    return Tree.adjoin(leftTree,rightTree);
		}
		skipped += treesInBranch;
	    }
	    return null;
	} else {
	    return new Tree(label);
	}
    }

     private class AllTreesIterable implements Iterable<Tree> {

	public final Edge edge;

	public AllTreesIterable(Edge e) {
	    edge = e;
	}
	
	private class AllTreesIterator implements Iterator<Tree> {
	    private int treesRemaining = edge.countTrees();
     	    public boolean hasNext() { return treesRemaining > 0; }

	    public Tree next () { 
	    	assert(treesRemaining > 0);
	    	treesRemaining --;
	    	return edge.getTree(treesRemaining);
	    }

	    public void remove() {}

	    
	}
	
	public Iterator<Tree> iterator () {
	    return new AllTreesIterator();
	}
	
};


    /**
     * Generate all trees from the current edge
     *
     * @return Iterable suitable for use with Java's new style for loop
     */

    public Iterable<Tree> allTrees() {
	//  Assignment 2.4 (extra credit) : your code here
	//  Arrange things so that you return an iterator
	//  that gives access to all the trees (not just the
	//  first one)
	// partially done.
	return new AllTreesIterable(this);
    }

    /**
     * Equality tester that ignores the predecessor field
     * 
     * @param o the object against which this should be compared for equality
     */


    public boolean equals(Object o) {
	Edge other = (Edge) o;
	return (getLeft() == other.getLeft() && 
			getRight() == other.getRight() && 
			getLabel().equals(other.getLabel()) && 
			needed.equals(other.needed));
    } 


    /**
     * Comparison method that ignores the predecessor field, as needed for sets.
     * 
     * @param other the Edge against which this should be compared for equality
     */
    
    @Override	
    public int compareTo(Edge other) {
	int x = getLeft()-other.getLeft();
	if(x != 0) 
	    return x;
	x = getRight() - other.getRight();
	if(x != 0) 
	    return x;
	x = getLabel().compareTo(other.getLabel());
	if(x != 0) 
	    return x;	
	x = needed.size() - other.needed.size();
	if(x != 0) 
	    return x;	
	for(int i = 0; i < needed.size(); i++) {
	    x = needed.get(i).compareTo( other.needed.get(i));
	    if(x != 0) 
		return x;	
	}
	return 0;
    }


    /**
     * provide edge as string
     */
    String asString() {
	if (iscomplete())
	    return  label + ":" + left + "-" + right; 
	else
	    return label + ":" + left + "-" + right + "/" + needed;
    }


	/**
	 * @return the predecessors
	 */
	public SortedSet<TraceEntry> getPredecessors() {
		return predecessors;
	}




};