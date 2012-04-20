from nfa import *

letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

# a(a|b)x*
reg0 = char_nfa ('a') \
       .add_next_state (or_nfa (char_nfa ('a'), char_nfa ('b'))) \
       .add_next_state (asterix_nfa (char_nfa ('x'))) \
       .add_next_state (done_nfa ())
regexp0 = 'a(a|b)x*' 

# (a|b)*
reg1 = asterix_nfa(or_nfa(char_nfa('a'), char_nfa('b')))\
       .add_next_state(done_nfa())
regexp1 = '(a|b)*'

# (ab*|bb)
reg2 = or_nfa (char_nfa ('a').add_next_state (asterix_nfa(char_nfa('b'))),\
               char_nfa ('b').add_next_state (char_nfa('b')))\
       .add_next_state(done_nfa())
regexp2 = '(ab*|bb)'

#((c*)*)*
reg3 = asterix_nfa(asterix_nfa(asterix_nfa(char_nfa('c')))).add_next_state(done_nfa())
regexp3 = '((c*)*)*'

#((c|a)|(b|xxb*))
reg4 = or_nfa (or_nfa(char_nfa ('c'), char_nfa ('a')),\
               or_nfa(char_nfa ('b'),\
                      char_nfa ('x').add_next_state(char_nfa('x'))\
                      .add_next_state(asterix_nfa(char_nfa('b')))))\
       .add_next_state(done_nfa())
regexp4 = '((c|a)|(b|xxb*))'

#(((a|b)|c)|x)
reg5 = or_nfa (or_nfa (or_nfa (char_nfa ('a'), char_nfa ('b')),\
                       char_nfa('c')),\
               char_nfa('x'))\
       .add_next_state(done_nfa())
regexp5 = '(((a|b)|c)|x)'

# (x|(a|(b|c*)*)*)
reg6 = or_nfa (char_nfa ("x"),\
       asterix_nfa (or_nfa (char_nfa ('a'), \
                            asterix_nfa (or_nfa (char_nfa ('b'),\
                                                 asterix_nfa (char_nfa ('c')))))) \
       ).add_next_state (done_nfa ())
regexp6 = '(x|(a|(b|c*)*)*)'

# x*(a|c)
reg7 = asterix_nfa (char_nfa('x'))\
       .add_next_state (or_nfa (char_nfa('a'), char_nfa ('c')))\
       .add_next_state (done_nfa ())
regexp7 = 'x*(a|c)'

regexp8 = 'abb|aab'

regexp9 = '(a|b)*abb'

regexp10 = '(ab|a)*'

merge([det(parse("a*"), letters), det(parse("aa"), letters), det(parse("a"), letters), det(parse("ab"), letters)])
quit()

regexp_list = [regexp0, regexp1, regexp2, regexp3, regexp4, regexp5, regexp6, regexp7, regexp8, regexp9]
execute ("aaabb", regexp_list)

#reg = regexp7
#print reg
#f = parse (reg)
#for dfa in det(f, letters):
#    if dfa is not None:
#        print dfa
#        for p in dfa.paths:
#            print "\t", p, "->", dfa.paths[p]

# vim: set ts=4 sw=4 sts=4 et
