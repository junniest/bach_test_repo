from nfa import *

def print_res(result, regexp_list):
    if result is None:
        print "Nothing accepted"
    else:
        print "Accepted regexp", regexp_list[result]

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
(result, auto, time[0]) = execute ("abb", regexp_list)
print_res(result, regexp_list)
(result, auto, time[1]) = execute ("ccc", regexp_list)
print_res(result, regexp_list)
(result, auto, time[2]) = execute ("abcbcbcbcbcbcxxxxxx", regexp_list)
print_res(result, regexp_list)
(result, auto, time[3]) = execute ("aaaaaaad", regexp_list)
print_res(result, regexp_list)
(result, auto, time[4]) = execute ("abcbbbbbbb", regexp_list)
print_res(result, regexp_list)
(result, auto, time[5]) = execute ("xxxxxxc", regexp_list)
print_res(result, regexp_list)
(result, auto, time[6]) = execute ("aabbabb", regexp_list)
print_res(result, regexp_list)
(result, auto, time[7]) = execute ("xxbbbbb", regexp_list)
print_res(result, regexp_list)
(result, auto, time[8]) = execute ("ab", regexp_list)
print_res(result, regexp_list)
(result, auto, time[9]) = execute ("cx", regexp_list)
print_res(result, regexp_list)

time_all = sum(time)
print "Execution time", time_all

# vim: set ts=4 sw=4 sts=4 et
