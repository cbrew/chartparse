package edu.osu.nlp.chartparser;
import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintStream;
import java.util.Arrays;
import java.util.Collections;
import java.util.ResourceBundle;
import java.util.Set;


/**
 * Driver for the OSU CSE 732 chart parser
 *
 * @author Chris Brew
 * @version 0.5
 */
public class RunChart {

    /**
     * run parser
     */


    private static boolean printTrees;
    private static PrintStream treesOut;

    private static void parse(String [] words) throws IOException { 
	
	

	Set<String> topCats = Collections.singleton("S");
	
	Chart c = new Chart(words,topCats);


	treesOut.println(Arrays.asList(words));
	for(Edge e: c.solutions(topCats)) {
	    int treeNum = 0;
	     if(printTrees) 
	    	for(Tree t: e.allTrees()){
		    treesOut.println("Tree: " + treeNum);
		    treeNum++;
		    treesOut.println(t.asString());
		}
	}
    }


    /**
     * Runs the chart parser
     * @param args  ignored
     */

	
	public static void main(String [] args) throws IOException {
       String sentenceFile = "sentences.txt";
       String line;
       treesOut = System.out;
       BufferedReader in  = new BufferedReader(new FileReader(sentenceFile));
       ResourceBundle bundle = ResourceBundle.getBundle("Chart");
       printTrees = bundle.getString("parser.printTrees").equals("true");
       
       
       while((line = in.readLine()) != null) {
    	   String [] words = line.trim().split(" +");
		   	parse(words);

		   
       }	
   }
};


