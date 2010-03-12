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
    /**
     *
     */
    public   final String parent;
    /**
     *
     */
    public   final List<Tree> children;
    /**
     *
     */
    public static final List<Tree> empty = Collections.emptyList();


    //constructor for internal node
    /**
     *
     * @param p
     * @param cs
     */
    public Tree(String p,List<Tree> cs) {
	parent = p;
	children = cs;
    }

    /**
     *
     * @param p
     * @param cs
     */
    public Tree(String p,Tree [] cs) {
	this(p,Arrays.asList(cs));
    }

    // constructor for leaf
    /**
     *
     * @param p
     */
    public Tree(String p)
    { this(p,empty); }

    // constructor for adjoining two trees
    /**
     *
     * @param p
     * @param c
     * @return
     */
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

    /**
     *
     * @return
     */
    public String asString() {
	StringBuilder s = new StringBuilder();
	treestring2(s,0);

	return s.toString();
    }
    
    /**
     *
     * @param args
     */
    public static void main(String [] args) {
	Tree [] subtrees = {new Tree("np"),new Tree("vp")}; 
	Tree t = new Tree("s",subtrees);

	System.out.println(t.asString());
    }

}