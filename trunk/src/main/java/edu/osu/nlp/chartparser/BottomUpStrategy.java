package edu.osu.nlp.chartparser;

import java.util.Set;

/**
 * A bottom-up strategy for the parser.
 */
public class BottomUpStrategy extends Strategy {


    BottomUpStrategy(final Chart ch) {
        super(ch);
    }

    /**
     * Initialization for bottom-up strategy.
     * @param words the sentence to be tagged
     * @param topCats the allowable root categories.
     */
    @Override
    public final void initialize(final String[] words, final Set<String> topCats) {
        int i = 0;
        for (String word : words) {
            getMyChart().agenda.add(Edges.lexical(word, i));
            i++;
        }
    }

    /**
     * the bottom-up strategy predicts rule invocations here.
     *
     * @param label the label of the complete edge
     * @param position the position at which the predictions
     *  should be made.
     */
    @Override
    public final void predictFromComplete(final String label, final int position) {
        for (Rule r : getMyChart().rules) {
            if (r.getRhs().get(0).equals(label)) {
                getMyChart().agenda.add(Edges.empty(r, position));
            }
        }
    }

    /**
     * The bottom-up strategy doesn't make predictions from
     * partials, but it does pair them with the corresponding
     * completes.
     *
     * @param edge the edge from which predictions should be made
     */
    @Override
    public final void predictFromPartial(final Edge edge) {
        int right = edge.getRight();
        Set<Edge> cs = getMyChart().completes.get(right);
        getMyChart().pairwithcompletes(edge, cs);
    }
}
