package edu.osu.nlp.chartparser;
import java.io.*;
import java.util.Collection;
import java.util.ArrayList;
import java.util.Random;

/**
 * The OSU CSE 732 generator
 *
 * @author Chris Brew
 * @version 0.5
 */
public class   Generator {


    private static final Collection<Rule> rules = Rules.grammar("grammar.txt"); // hard-wired
    private static final Random rnd = new Random(0x123456);  // always use same seed, for ease of debugging

    /**
     * Create a generator
     */
    public Generator() {

    }

    /**
     * randomly generate the next tree based on a given lhs.
     *  
     *       
     * @param lhs to generate from
     */

    public Tree nextTree(String lhs) {
	

	// look up relevant rules for lhs. 
	// with a different organization of the grammar this
	// would be a hash table lookup, and maybe a bit faster
	ArrayList<Rule> relevant = new ArrayList<Rule> ();
	for(Rule r: rules) {
	    if(r.lhs.equals(lhs)) {
		relevant.add(r);
	    }
	}

	if(relevant.size() == 0) {
	    // we have a leaf
	    return new Tree(lhs);
	} else {
	    // we have an internal node whose subtrees must be generated
	    ArrayList<Tree> subtrees = new ArrayList<Tree>();
	    Rule r = relevant.get(rnd.nextInt(relevant.size()));
	    for(String clhs: r.rhs) {
		subtrees.add(nextTree(clhs));
	    }			  
	    return new Tree(lhs,subtrees);
	}
    }

   public static void main (String [] args) throws IOException {

       Generator g = new Generator();
       Integer n = Integer.parseInt(args[0]);

       for(int i = 0; i < n; i++)
	   System.out.println(g.nextTree("S").asString());
   }


};