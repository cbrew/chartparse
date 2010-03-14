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
import java.util.Collections;
import java.util.LinkedList;
import java.util.List;
import java.util.Queue;
import java.util.Set;
import java.util.TreeSet;
import java.util.ResourceBundle;
import java.lang.reflect.Constructor;



/** 
 * CSE 732 Chart Parser
 * This is a bottom-up chart parser for a fragment of English.
 * It uses the active chart datastructure. The design is based
 * on Steve Isard's <code>LIB CHART</code>, a teaching tool (written in 1983) that
 * comes with the wonderful Poplog AI development environment.
 *
 * The key datastructures are containers for partial and complete edges, called 
 * partials and completes below. Completes is an array of sets such that all the
 * edges starting at position <code>i</code> of the input string are stored in
 * <code>completes[i]</code>. Partials is the same, except that <code>partial[i]</code>
 * stores all the edges that <b>end</b> at <code>i</code>. This layout is designed
 * to make application of the fundamental rule of chart parsing transparent.
 *
 * @see <a href="http://www.poplog.org/">http://www.poplog.org/</a> 
 * @see <a href="http://www.poplog.org/gospl/packages/pop11/lib/chart.p">http://www.poplog.org/gospl/packages/pop11/lib/chart.p </a> 
 * @author Chris Brew
 */
public class Chart {

    // store for complete edges
    private final ArrayList<Set<Edge>> completes;

    // store for partial edges
    private final ArrayList<Set<Edge>> partials;

    // store for agenda
    private final Queue<Edge> agenda;
    
    // N is the length of the input string
    private final int N;
    
    // rules is the grammar used 
    private final List<Rule> rules;
    private String [] sentence;

    // statistics

    public int numCompleteEdges = 0, numPartialEdges = 0;
    

    private Strategy strategy = null;

    private EdgeMonitor monitor = null;

    private boolean bottomUp = true;
     
    /**
     * Implements a chart parser
     * @param words the words to be parsed
     * @param topCats
     */
    
    
    
    
    public Chart(String [] words,Set<String> topCats)  {
    		
    	ResourceBundle bundle = ResourceBundle.getBundle("Chart");
    	String grammarFile = bundle.getString("parser.grammar");

		bottomUp = bundle.getString("parser.bottomUp").equals("true");	
	
		try {
			if(bundle.getString("parser.monitorEdges").equals("true")) {
				Class<?> consClass = Class.forName(bundle.getString("parser.monitorClass"));
				Class<?> [] argClasses = {};
				Object [] args = {};
				Constructor<?> cons = (Constructor<?>) consClass.getConstructor(argClasses);
				monitor = (EdgeMonitor) cons.newInstance(args);
			} 
		} catch (Exception e) {
			System.out.println("Failed to find edge monitor class as configured: exiting!");
			System.exit(-1);
		}
	


		N = words.length;

		completes = new ArrayList<Set<Edge>>(N +1);
		partials = new ArrayList<Set<Edge>>(N +1);
		sentence = words;
		agenda = new LinkedList<Edge>();

		// read rules from grammar file.
		
		if(bundle.getString("parser.useInternalGrammar").equals("true"))
			rules = Rules.english();
		else
			rules = Rules.grammar(grammarFile);
	
	
   
		for(int i =0; i <= N; i++){
			completes.add(new TreeSet<Edge>());
			partials.add(new TreeSet<Edge>());
		}
	
		if(bottomUp) {
			strategy = new BottomUpStrategy(this);
		} else {
			strategy = new TopDownStrategy(this);
		} 	
	 
	strategy.initialize(words,topCats);
	while(! agenda.isEmpty()) {
	    Edge e = agenda.remove();
	    boolean incorporated = strategy.incorporate(e);
	    if(monitor != null && incorporated){
	    	monitor.note(e);
	    }

	}
		
	
    }

    /**
     * Find the edges that span the input string and have one of the desired categories
     *
     * @param topCats the desired categories (often this will be a singleton set having element "S")
     * @return the edges having the desired property
     */
    public Set<Edge> solutions(Set<String> topCats) {
	Set<Edge> dest = new TreeSet<Edge>();

	for(Edge e : completes.get(0))
	    if(topCats.contains(e.getLabel()) && e.getLeft() == 0 && e.getRight() == N)
		dest.add(e);
	return dest;
    }
    // the procedure that pairs a given complete with the partials that abut it
    // and pushes the results onto the agenda
    private void pairwithpartials(Set<Edge> partials,Edge complete){
	for(Edge partial: partials) {
	    if(partial.firstNeeded().equals(complete.getLabel())) {
		agenda.add(Edges.fundamental(partial, complete));
	    }
	}
    }

    // the procedure that pairs a given partial with the completes that abut it
    // and pushes the results onto the agenda
    private void pairwithcompletes(Edge partial,Set<Edge> completes){
	for(Edge complete: completes) {
	    if(partial.firstNeeded().equals(complete.getLabel())) {
		agenda.add(Edges.fundamental(partial, complete));
	    }
	}
    }
    /**
     * A class providing a partial implementation of parsing strategies.
     * 
     */
    public abstract class Strategy {
        /**
         *
         */
        protected Chart myChart;
	/**
	 * called to set up the parser with a string of words
         *
         * @param words
         * @param topCats
         */
	public abstract void initialize(String [] words,Set<String> topCats);
	/**
	 * called when a complete edge is added to the chart
	 * in order to do any necessary prediction of rules
	 * that might apply to it
         *
         * @param label
         * @param position
         */
	public abstract void predictFromComplete(String label,int position);
	
	/**
	 * called when a partial edge is added to the chart
         *
         * @param e
         */
	public abstract void predictFromPartial(Edge e);


	/**
	 * The main driver procedure that adds edges to the chart and
	 * causes the actions dictated by the strategy to fire
         *
         * @param e
         * @return
         */
	public boolean incorporate(Edge e) {
	    TreeSet<Edge> edges;

	    if(e.iscomplete()) {
		edges = (TreeSet<Edge>) completes.get(e.getLeft());
	    } else { 
		edges = (TreeSet<Edge>) partials.get(e.getRight());
	    }

	    if(edges.contains(e)) {
	    	Edge oldEdge = edges.tailSet(e).first();
	    	oldEdge.getPredecessors().addAll(e.getPredecessors());
	    	return false;
	    } else {
		edges.add(e);
		if(e.iscomplete()){
		    numCompleteEdges ++;
		    predictFromComplete(e.getLabel(),e.getLeft());
		    pairwithpartials(partials.get(e.getLeft()),e);
		} else {
		    assert(e.ispartial());
		    numPartialEdges++;
		    predictFromPartial(e);
		}
		return true;
	    }
   
	}
    };

    /**
     * A top down strategy for the parser
     */
    
    public class TopDownStrategy extends Strategy {
    	
    	TopDownStrategy(Chart ch){myChart = ch;}
    	
	@Override public void initialize(String [] words,Set<String> topCats) {
	    for(Rule r: rules)
		if(topCats.contains(r.lhs))
		    agenda.add(Edges.empty(r,0));
	}

	/**
	 * A top down strategy does not need to spawn empty edges from
	 * complete edges, because all the relevant ones are generated by
	 * top down prediction.
         *
         * @param label
         * @param position
         */
	@Override public void predictFromComplete(String label,int position) { /* nothing needed here */ }
	
	/**
	 * The procedure that implements the predict and scan parts 
	 * of Earley's algorithm.
         *
         * @param e
         */
	@Override public void predictFromPartial(Edge e) {
	    predict(e);	    
	    scan(e);
	}

	private void scan(Edge e) {
	    int position = e.getLeft();

	    if(position < N && e.firstNeeded().equals(sentence[position])) {
		Edge lex = Edges.lexical(sentence[position],position);
		agenda.add(lex);
	    } 
	}


	private void predict(Edge e) {

	    // this is very unguided, makes many hypotheses without looking at
	    // input string.
	    for(Rule r: rules)
		if(r.lhs.equals(e.firstNeeded()))
		    agenda.add(Edges.empty(r,e.getRight()));
	
	}
    };

    /**
     * A bottom-up strategy for the parser
     */

    public class BottomUpStrategy extends Strategy {
    	
    	BottomUpStrategy(Chart ch){myChart = ch; }
	@Override
	public void initialize(String [] words,Set<String> topCats) {
		int i = 0;
		for(String word: words) {
		    agenda.add(Edges.lexical(word,i));
		    i++;
		}
	    }
	/**
	 * the bottom-up strategy predicts rule invocations here.
         *
         * @param label
         * @param position
         */
	
        @Override
        public void predictFromComplete(String label,int position) {
	    for(Rule r: rules) {
		if(r.rhs.get(0).equals(label)) {
		    agenda.add(Edges.empty(r,position));
		}
	    }
	}

	/**
	 * The bottom-up strategy doesn't make predictions from
	 * partials, but it does pair them with the corresponding
	 * completes
         *
         * @param edge
         */
	@Override public void predictFromPartial(Edge edge) {
	    pairwithcompletes(edge,completes.get(edge.getRight()));
	    } 
    };


   

    /**
     *
     * @param args
     */
    public static void main(String [] args)  {

	Set<String> topCats = Collections.singleton("S");

	Chart c = new Chart(args,topCats);

	for(Edge e: c.solutions(topCats)){
				
            Tree t = e.firstTree();

            if(t != null)
		System.out.println(t.asString());
	}
    }   
}