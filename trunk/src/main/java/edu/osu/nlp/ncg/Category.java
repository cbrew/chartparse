/*
 *  Copyright 2010 cbrew.
 *
 *  Licensed under the Apache License, Version 2.0 (the "License");
 *  you may not use this file except in compliance with the License.
 *  You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 *  Unless required by applicable law or agreed to in writing, software
 *  distributed under the License is distributed on an "AS IS" BASIS,
 *  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *  See the License for the specific language governing permissions and
 *  limitations under the License.
 *  under the License.
 */

package edu.osu.nlp.ncg;

import java.util.Collections;
import java.util.List;

/**
 *
 * @author cbrew
 */
public class Category {
    /**
     * the final result.
     */
    private String functor;
    /**
     * the arguments that must be consumed to produce a final result.
     **/
    private List<Category> args;


    
    public Category(String f){
        functor = f;
        args = Collections.emptyList();
    }


    

}
