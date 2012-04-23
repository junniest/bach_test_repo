from nfa import *

token_regexp_1 = [t_id('f'), t_lbrace(), t_m_lbrace(), t_expr(), 
                t_delim_com(), t_m_lbrace(), t_int(), t_m_pipe(), t_real(), t_m_rbrace(), t_m_rbrace(), 
                t_m_asterisk(), t_rbrace(), t_m_end(), t_id()]
# equivalent to {match} {id} \( ( {expr} \, ( {int} | {real} ) ) * \) {/match}

token_list_1 = [t_id('f'), t_lbrace(), t_real(), t_delim_com(), t_int(), t_rbrace()]

(result, auto, time) = execute(token_list_1, [token_regexp_1])
print result, time

for i in auto:
    print i

# vim: set ts=4 sw=4 sts=4 et
