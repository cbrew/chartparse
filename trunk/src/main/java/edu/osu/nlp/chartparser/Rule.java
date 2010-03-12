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

import java.util.List;
import java.util.Arrays;

/**
 * Data structure representing phrase structure rules
 * 
 * @author Chris Brew
 * @version 0.5
 */

public class Rule  {
    public String lhs;
    public List<String> rhs;
  
    public Rule(String label,String rstr) {
	lhs = label;
	rhs = Arrays.asList(rstr.trim().split("[ \t]+")); // split by space
    }

    

}