package edu.osu.nlp.chartparser;

/**
 * Interface for classes that monitor the incorporation of edges
 */
public interface EdgeMonitor {
    void note(Edge e);
}