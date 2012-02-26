from nfa import *


# a(a|b)x*
reg0 = char_nfa ('a') \
       .add_next_state (or_nfa (char_nfa ('a'), char_nfa ('b'))) \
       .add_next_state (asterix_nfa (char_nfa ('x'))) \
       .add_next_state (done_nfa ())
postf_reg0 = 'a(ab|).x*.' 

# (a|b)*
reg1 = asterix_nfa(or_nfa(char_nfa('a'), char_nfa('b')))\
       .add_next_state(done_nfa())
postf_reg1 = '(ab|)*'

# (ab*|bb)
reg2 = or_nfa (char_nfa ('a').add_next_state (asterix_nfa(char_nfa('b'))),\
               char_nfa ('b').add_next_state (char_nfa('b')))\
       .add_next_state(done_nfa())
postf_reg2 = 'ab*.bb.|'

#((c*)*)*
reg3 = asterix_nfa(asterix_nfa(asterix_nfa(char_nfa('c')))).add_next_state(done_nfa())
postf_reg3 = 'c***'

#((c|a)|(b|xxb*))
reg4 = or_nfa (or_nfa(char_nfa ('c'), char_nfa ('a')),\
               or_nfa(char_nfa ('b'),\
                      char_nfa ('x').add_next_state(char_nfa('x'))\
                      .add_next_state(asterix_nfa(char_nfa('b')))))\
       .add_next_state(done_nfa())
postf_reg4 = '(ca|)(b(xx.b*.)|)|'

#(((a|b)|c)|x)
reg5 = or_nfa (or_nfa (or_nfa (char_nfa ('a'), char_nfa ('b')),\
                       char_nfa('c')),\
               char_nfa('x'))\
       .add_next_state(done_nfa())


# (a | ( b | c * ) ) *
reg6 = or_nfa (char_nfa ("x"),\
       asterix_nfa (or_nfa (char_nfa ('a'), \
                            asterix_nfa (or_nfa (char_nfa ('b'),\
                                                 asterix_nfa (char_nfa ('c')))))) \
       ).add_next_state (done_nfa ())


# x* a | c
f = asterix_nfa (char_nfa('x'))\
    .add_next_state (or_nfa (char_nfa('a'), char_nfa ('c')))\
    .add_next_state (done_nfa ())

f = reg6

#enumerate_states (f)
f.xprint ()

print

for dfa in det(f, 'abcxz'):
    if dfa is not None:
        print dfa
        for p in dfa.paths:
            print "\t", p, "->", dfa.paths[p]

# vim: set ts=4 sw=4 sts=4 et

