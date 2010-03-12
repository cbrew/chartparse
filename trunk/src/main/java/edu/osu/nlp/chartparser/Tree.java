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

import java.util.Arrays;
import java.util.List;
import java.util.ArrayList;
import java.util.Collections;

/**
 * The data structure for a syntax tree
 *
 * @author Chris Brew
 * @version 0.5
 */

public class Tree {
    public   final String parent;
    public   final List<Tree> children;
    public static final List<Tree> empty = Collections.emptyList();


    //constructor for internal node
    public Tree(String p,List<Tree> cs) {
	parent = p;
	children = cs;
    }

    public Tree(String p,Tree [] cs) {
	this(p,Arrays.asList(cs));
    }

    // constructor for leaf
    public Tree(String p) 
    { this(p,empty); }

    // constructor for adjoining two trees
    public static Tree adjoin(Tree p, Tree c) {
	List<Tree> newchildren = new ArrayList<Tree>(p.children);
	newchildren.add(c);
	Tree tr = new Tree (p.parent,newchildren);
	
	return tr;
    }



    private void treestring2(StringBuilder s,int tab) {
	s.append('\n');
	for(int i = 0; i < tab; i++)
	    s.append(' ');
	s.append('(');
	if(children.size() == 1 && children.get(0).children.size() == 0) {
	    s.append(parent + " " + children.get(0).parent);
	} else {
	    s.append(parent);
	    for(Tree child: children)
		child.treestring2(s,tab+1);
	}
	s.append(')');
    }


    @SuppressWarnings("unused")
	private void treestring(StringBuilder s,int tab) {
	for(int i = 0; i < tab; i++)
	    s.append(' ');
	if(children.size() == 1 && children.get(0).children.size() == 0) {
	    s.append(parent + " " + children.get(0).parent + "\n");
	} else {
	    s.append(parent);
	    s.append('\n');
	    for(Tree child: children)
		child.treestring(s,tab+1);
	}
    }

    public String asString() {
	StringBuilder s = new StringBuilder();
	treestring2(s,0);

	return s.toString();
    }
    
    public static void main(String [] args) {
	Tree [] subtrees = {new Tree("np"),new Tree("vp")}; 
	Tree t = new Tree("s",subtrees);

	System.out.println(t.asString());
    }

}