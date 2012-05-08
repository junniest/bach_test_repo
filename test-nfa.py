from nfa import *

def test_case_0 ():
    """ A test for context switching and matching (depth = 2). """
    regexp_1 = [t_m_start(), t_id(), t_lbrace(), t_m_lbrace(), t_real(),
                t_m_pipe(), t_int(), t_m_rbrace(), t_m_asterisk(), t_rbrace(),
                t_m_end()]
    # {match} {id} '(' ( {real} | {int} ) * ')' {\match}

    regexp_2 = [t_context_start(), t_m_start(), t_id(), t_lbrace(), t_real(),
                t_rbrace(), t_m_end()]
    # {
    #     {match} {id} '(' {real} ')' {\match}
    
    list_1 =   [t_id('g'), t_lbrace(), t_real(5.78), t_rbrace(), 
                t_context_start()]
    #     g(5.78) - Should match #1
    #     {
    
    regexp_3 = [t_m_start(), t_id(), t_lbrace(), t_real(), 
                t_rbrace(), t_m_end()]
    #         {match} {id} '(' {real} ')' {\match}
    
    list_2 =   [t_id('e'), t_lbrace(), t_real(4.0), t_rbrace()]
    #         e(4.0) - Should match #2
    
    list_3 =   [t_id('e'), t_lbrace(), t_real(4.0), t_int(5), t_rbrace(),
                    t_context_end()]
    #         e(4.0 5) - Should match #0
    #     }

    list_4 =   [t_id('d'), t_lbrace(), t_real(3.4), t_rbrace(), t_context_end()]
    #     d(3.4) - Should match #1
    # }
    
    execute (regexp_1 + regexp_2 + list_1 + regexp_3 + list_2 + list_3 + list_4)


def test_case_1 ():
    """ A test for context switching and matching (depth = 1). """
    regexp_1 = [t_m_start(), t_id(), t_lbrace(), t_real(), t_m_asterisk(),
                t_rbrace(), t_m_end()]
    # {match} {id} '(' {real} * ')' {\match}

    list_1 =   [t_context_start(), t_id('f'), t_lbrace(), t_real(3.5),
                t_rbrace()]
    # {
    #     f(3.5) - Should match #0

    regexp_2 = [t_m_start(), t_id(), t_lbrace(), t_real(), t_rbrace(),
                t_m_end()]
    #     {match} {id} '(' {real} ')' {\match}
    
    list_2 =   [t_id('g'), t_lbrace(), t_real(5.78), t_rbrace()]
    #     g(5.78) - Should match #1

    list_3 =   [t_id('e'), t_lbrace(), t_real(4.0), t_real(5.8), t_rbrace(),
                t_context_end()]
    #    e(4.0 5.8) - Should match #0
    # }

    list_4 =   [t_id('d'), t_lbrace(), t_real(3.4), t_rbrace()]
    # d(3.4) - Should match #0

    execute (regexp_1 + list_1 + regexp_2 + list_2 + list_3 + list_4)


def test_case_2 ():
    """ A test for correct priorities. """
    regexp_1 = [t_m_start(), t_id(), t_lbrace(), t_rbrace(), t_m_end()]
    # {match} {id} '(' ')' {\match}

    regexp_2 = [t_m_start(), t_id(), t_lbrace(), t_real(), t_m_asterisk(), 
                t_rbrace(), t_m_end()]
    # {match} {id} '(' {real} * ')' {\match}

    regexp_3 = [t_m_start(), t_id(), t_lbrace(), t_real(), t_rbrace(),
                t_m_end()]
    # {match} {id} '(' {real} ')' {\match}

    list_1 =   [t_id('f'), t_lbrace(), t_rbrace()]
    # f() - Should match #0
    
    list_2 =   [t_id('f'), t_lbrace(), t_real(6.1), t_rbrace()]
    # f(6.1) - Should match #1

    execute (regexp_1 + regexp_2 + regexp_3 + list_1 + list_2)


def test_case_3 ():
    """ Another test for correct priorities. """
    regexp_1 = [t_m_start(), t_id(), t_lbrace(), t_m_lbrace(), t_expr(), 
                t_m_lbrace(), t_delim_com(), t_int(), t_m_pipe(), 
                t_delim_com(), t_real(), t_m_rbrace(), t_m_asterisk(), 
                t_m_rbrace(), t_rbrace(), t_m_end()]
    # {match} {id} '(' ( {expr} ( ',' {int} | ',' {real} ) * ) ')' {/match}

    regexp_2 = [t_m_start(), t_id(), t_lbrace(), t_m_lbrace(), t_expr(), 
                t_m_lbrace(), t_delim_com(), t_int(), t_m_pipe(), 
                t_delim_com(), t_real(), t_m_rbrace(), t_m_rbrace(), 
                t_m_asterisk(), t_rbrace(), t_m_end()]
    # {match} {id} '(' {expr} * ')' {/match}

    list_1 = [t_id('f'), t_lbrace(), t_rbrace(), t_delim_col()]
    # f() - Should match #1

    list_2 = [t_id('g'), t_lbrace(), t_expr(), t_delim_com(), t_int(),
              t_rbrace()]
    # g(expr, int) - Should match #0
    
    list_3 = [t_id('e'), t_lbrace(), t_expr(), t_rbrace()]
    # e(expr) - Should match #0

    execute(regexp_1 + regexp_2 + list_1 + list_2 + list_3)


def test_case_4 ():
    """ A test for token types. """
    regexp_1 = [t_m_start(), t_m_lbrace(), t_real(), t_m_pipe(), t_int(),
                t_m_rbrace(), t_delim_col(), t_m_end()]
    # {match} {real} ';' {\match}

    regexp_2 = [t_m_start(), t_int(), t_delim_com(), t_m_end()]
    # {match} {int} ',' {\match}

    list_1 = [t_int(), t_delim_col()]
    # 5; - Should match #0

    list_2 = [t_int(2), t_delim_com()]
    # 2, - Should match #1
    
    list_3 = [t_expr('4 + 13'), t_delim_col()]
    # 4 + 13; - Should not match

    execute(regexp_1 + regexp_2 + list_1 + list_2 + list_3)


def execute_test (test_no):
    globals() ['test_case_' + str (test_no)]()


if __name__ == "__main__":
    for i in xrange(5):
        print
        print "================"
        execute_test(i)
        print "================"

# vim: set ts=4 sw=4 sts=4 et