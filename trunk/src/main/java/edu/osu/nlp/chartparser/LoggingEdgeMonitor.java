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

/**
 * Fixture allowing us to see edges printed out as they are made.
 * @author cbrew
 */
public class LoggingEdgeMonitor implements EdgeMonitor {
    /**
     * keeps track of the number of edges seen.
     */
    private int edgeno = 1;

    /**
     * notice when an edge is incorporated.
     * @param e the edge just seen
     */
    @Override
    public final void note(final Edge e) {
        System.out.println(edgeno + ":" + e.asString());
        edgeno++;
    }
}



