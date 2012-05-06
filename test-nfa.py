from nfa import *

regexp_1 = [t_m_start(), t_id(), t_lbrace(), t_rbrace(), t_m_end()]
regexp_2 = [t_m_start(), t_id(), t_lbrace(), t_real(), t_m_asterisk(), 
            t_rbrace(), t_m_end()]
regexp_3 = [t_m_start(), t_id(), t_lbrace(), t_real(), t_rbrace(), t_m_end()]
list_1 = [t_id('f'), t_lbrace(), t_rbrace()]

execute (regexp_1 + regexp_2 + regexp_3 + list_1)

quit ()

token_regexp_1 = [t_m_start(), t_id('f'), t_lbrace(), t_m_lbrace(), t_expr(), 
                  t_m_lbrace(), t_delim_com(), t_int(), t_m_pipe(), 
                  t_delim_com(), t_real(), t_m_rbrace(), t_m_rbrace(), 
                  t_m_asterisk(), t_rbrace(), t_m_end()]
# equivalent to {match} {id:f} \( ( {expr} ( \, {int} | \, {real} ) ) * \) 
# {/match}
# id 'f', left bracket, obligatory parameter 'expr', comma, non-obligatory 
# parameters 'int' or 'real', comma, right bracket

token_regexp_2 = [t_m_start(), t_id(), t_lbrace(), t_m_lbrace(), t_expr(), 
                  t_m_lbrace(), t_delim_com(), t_int(), t_m_pipe(), 
                  t_delim_com(), t_real(), t_m_rbrace(), t_m_rbrace(), 
                  t_m_asterisk(), t_rbrace(), t_m_end()]
# equivalent to {match} {id} \( ( {expr} ( \, {int} | \, {real} ) ) * \) 
# {/match}
# id, left bracket, obligatory parameter 'expr', comma, non-obligatory 
# parameters 'int' or 'real', comma, right bracket

token_list_1 = [t_id('f'), t_lbrace(), t_rbrace(), t_delim_col()]
# equivalent to f()

token_list_2 = [t_id('g'), t_lbrace(), t_real(), t_delim_com(), t_int(), 
                t_rbrace()]
# equivalent to g(real, int)

execute(token_regexp_1 + token_regexp_2 + token_list_1 + token_list_2)

# vim: set ts=4 sw=4 sts=4 et