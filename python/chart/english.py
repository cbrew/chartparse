"""An English grammar for chartparse.

This grammar was originally written by Steve Isard at the
University of Sussex. The vocabulary is designed to amuse
undergraduate Experimental Psychology students, hence the
references to pigeons and cages.

The grammar is almost entirely Steve's original. The only changes
are a few words, proper names, and the production:

    NP -> det Nn PP

which was changed to

    NP -> NP PP

The intent is to demonstrate ambiguous grouping of modifiers.

As in the original LIB CHART _[1], features on the categories
are ignored. There are three features used `case`, `num` and
`tr`. Thy could reasonably be handled in this file, via
compilation to a plain CFG, since their purpose is only
to enforce agreement.

References
----------

The original LIB CHART [1]_

.. [1] http://www.poplog.org/gospl/packages/pop11/lib/chart.p

"""

##
# Created 10 March 2014
# author: Chris Brew
# author: Stephen Isard
# license: Apache 2.0
##

from collections import defaultdict, namedtuple
import numpy.random as npr
import numpy as np


class Rule(namedtuple('Rule', ('lhs','rhs'))):

    """One production of a context-free grammar.

    Attributes
    ----------
    lhs: string
        The left hand side of the rule.
    rhs: list [string]
        The right hand side of the rule.


    Examples
    --------
    >>> r = Rule('s',('np','vp'))
    """

    def __repr__(self):
        return "Rule(lhs='{lhs}', rhs={rhs})".format(
                lhs=self.lhs,
                rhs=self.rhs)




    




class Grammar(object):

    """
    Class for creating grammars from text strings.

    Parameters
    ----------
    grammar: string
        the grammar rules, lines of the form `lhs -> rhs (|rhs)*`
    lexicon:  string
        the words, lines of the form `word category+`

    Examples
    --------
    >>> g = Grammar(RULES, WORDS)
    >>> g.grammar[0]
    Rule(lhs='S', rhs=['Np', 'Vp'])

    """

    def __init__(self, grammar, lexicon, state=None):
        """
        Create a grammar from strings.

        """
        self.state = (npr.RandomState(42) if state is None else state)
        self.grammar = self.__rulify(grammar) + self.__lexicalize(lexicon)

    def make_rule(self, lhs):
            return Rule(lhs=lhs, rhs=rhs)


    def __remove_balanced_brackets(self, string):
        r = []
        collecting = True
        for ch in string:
            if ch == "(":
                collecting = False
            elif ch == ")":
                collecting = True
            elif collecting:
                r.append(ch)
        return "".join(r)

    def __rulify(self, s):
        r = []
        s = self.__remove_balanced_brackets(s)
        lines = s.split('\n')
        for line in lines:
            lhs, rhs = line.split('->')
            lhs = lhs.split()[0]
            elems = rhs.split('|')
            r += [Rule(lhs=lhs, rhs=elem.split())
                  for elem in elems]
        return r

    def __lexicalize(self, string):
        string = self.__remove_balanced_brackets(string)
        lines = string.split("\n")
        rules = []
        for line in lines:
            a = line.split()
            w = a[0]
            r = "".join(a[1:])
            elems = r.split('|')
            for elem in elems:
                a = elem.split()
                rules.append(Rule(lhs=a[0], rhs=[w]))
        return rules


RULES = """S (num) -> Np(num case:subj) Vp(num) | S conj S
S (num) -> Np(num case:subj) cop(num) ppart
S(num) -> Np(num case:subj) cop(num) ppart passmarker Np(case:obj)
Np (num case) -> det(num) Nn(num) | Np Pp | pn(num case)
Np -> Np conj Np
Nn(num) -> n(num) | adj n(num)
Vp(num)  -> v(num tr:trans) Np(case:obj) | v(num tr:intrans) | cop(num) adj
Vp(num) -> Vp(num) Pp
Pp -> prep Np(case:obj)"""

WORDS = """det a(num:sing)
and conj
are cop(num:pl)
ball n (num : sing)
big adj
bitten ppart
blue adj
boy n(num:sing)
boys n(num:pl)
by passmarker | prep
cage n(num:sing) | v(num:pl tr:trans)
caged v(tr:trans) | ppart
cages n(num:pl) | v(num:sing tr:trans)
chris n(num:sing)
computer n(num:sing)
computers n(num:pl)
enormous adj
fifty det(num:pl)
four det(num:pl)
girl n(num:sing)
girls n(num:pl)
green adj
he pn(num:sing case:subj)
her pn(num:sing case:obj)
him pn(num:sing case:obj)
hit v(tr:trans) | ppart
hits v(tr:trans num:sing)
house n(num:sing)
in prep
is cop(num:sing)
little adj
mic pn(num:sing)
micro n(num:sing)
micros n(num:pl)
on prep
one n(num:sing) | pn(num:sing) | det(num:sing)
ones n(num:pl)
pdp11 n(num:sing)
pdp11s n(num:pl)
pigeon n(num:sing)
pigeons n(num:pl)
program n(num:sing) | v(num:pl tr:trans)
programmed v( tr:trans) | ppart
programs n(num:pl) | v(num:sing tr:trans)
punish v(num:pl tr:trans)
punished v( tr:trans) | ppart
punishes v(num:sing tr:trans)
ran v(tr:intrans)
rat n(num:sing)
rats n(num:pl)
red adj
reinforce v (num:pl tr:trans)
reinforced v ( tr:trans) | ppart
reinforces v (num:s tr:trans)
room n(num:sing)
rooms n(num:pl)
run v(tr:intrans num:pl)
runs v(tr:intrans num:sing)
scientists n(num:pl)
she pn(num:sing case:subj)
steve pn(num:sing)
stuart pn(num:sing)
suffer v(num:pl tr:intrans)
suffered v( tr:intrans)
suffers v(num:sing tr:intrans)
that det(num:sing)
the det
them pn(num:pl case:obj)
these det(num:pl)
they pn(num:pl case:subj)
those det (num:pl)
three det(num:pl)
two det(num:pl)
undergraduates n(num:pl)
universities n(num:pl)
university n(num:sing)
was cop(num:sing)
were cop(num:pl)"""


GRAMMAR = Grammar(RULES, WORDS)
