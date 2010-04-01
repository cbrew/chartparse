/**
 * Copyright (C) 2010 cbrew <cbrew@acm.org>
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *         http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */



package edu.osu.nlp.chartparser;


import java.util.Arrays;
import java.util.List;

/**
 * Data structure representing phrase structure rules.
 *
 * @author Chris Brew
 */
public class Rule {

    /**
     * the string representing the left hand side.
     */
    private String lhs;
    /**
     * a sequence of categories for the right hand side.
     */
    private List<String> rhs;

    /**
     * Create a rule from two strings.
     * @param label the left hand side of the rule
     * @param rstr  the right hand side of the rule
     */
    public Rule(final String label, final String rstr) {
        lhs = label;
        rhs = Arrays.asList(rstr.trim().split("[ \t]+"));    // split by space
    }

    /**
     * The obvious definition of equality for rules.
     * @param other the thing to compare against
     * @return true iff lhses equal and rhses equal
     */
    public final boolean equals(final Rule other) {
        return lhs.equals(other.lhs) && rhs.equals(other.rhs);
    }

    /**
     * @return the lhs
     */
    public final String getLhs() {
        return lhs;
    }

    /**
     * @param lh the lhs to set
     */
    public final void setLhs(final String lh) {
        this.lhs = lh;
    }

    /**
     * @return the rhs
     */
    public final List<String> getRhs() {
        return rhs;
    }

    /**
     * @param rh the rhs to set
     */
    public final void setRhs(final List<String> rh) {
        this.rhs = rh;
    }
}

