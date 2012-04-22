from nfa import *

regexp0 = 'a(a|b)x*' 

regexp1 = '(a|b)*'

regexp2 = '(ab*|bb)'

regexp3 = '((c*)*)*'

regexp4 = '((c|a)|(b|xxb*))'

regexp5 = '(((a|b)|c)|x)'

regexp6 = '(x|(a|(b|c*)*)*)'

regexp7 = 'x*(a|c)'

regexp8 = 'abb|aab'

regexp9 = '(a|b)*abb'

regexp10 = '(ab|a)*'

time = [0,0,0,0,0,0,0,0,0,0,0,0]

regexp_list = [regexp0, regexp1, regexp2, regexp3, regexp4, regexp5, regexp6, regexp7, regexp8, regexp9]
(a, time[0]) = execute ("abb", regexp_list)
(a, time[1]) = execute ("ccc", regexp_list)
(a, time[2]) = execute ("abcbcbcbcbcbcxxxxxx", regexp_list)
(a, time[3]) = execute ("aaaaaaad", regexp_list)
(a, time[4]) = execute ("abcbbbbbbb", regexp_list)
(a, time[5]) = execute ("xxxxxxc", regexp_list)
(a, time[6]) = execute ("aabbabb", regexp_list)
(a, time[7]) = execute ("xxbbbbb", regexp_list)
(a, time[8]) = execute ("ab", regexp_list)
(a, time[9]) = execute ("cx", regexp_list)

time_all = sum(time)
print "Execution time", time_all

# vim: set ts=4 sw=4 sts=4 et
