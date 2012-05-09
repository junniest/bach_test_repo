from nfa import *

def test_case_0 ():
    """ A test for context switching and matching (depth = 2). """
    
    regexp_1 = [t_m_start(), t_id(), t_lbrace(), t_m_lbrace(), t_real(),
                t_m_pipe(), t_int(), t_m_rbrace(), t_m_asterisk(), t_rbrace(),
                t_m_end()]
    # {match} {id} '(' ( {real} | {int} ) * ')' {\match}
    
    regexp_2 = [t_m_start(), t_id(), t_lbrace(), t_real(),
                t_rbrace(), t_m_end()]
    # {match} {id} '(' {real} ')' {\match}
    
    list_1 =   [t_id('g'), t_lbrace(), t_real(5.78), t_rbrace()]
    # g(5.78) - Should match #1
    
    regexp_3 = [t_m_start(), t_id(), t_lbrace(), t_real(), 
                t_rbrace(), t_m_end()]
    # {match} {id} '(' {real} ')' {\match}
    
    list_2 =   [t_id('e'), t_lbrace(), t_real(4.0), t_rbrace()]
    # e(4.0) - Should match #2
    
    list_3 =   [t_id('e'), t_lbrace(), t_real(4.0), t_int(5), t_rbrace()]
    # e(4.0 5) - Should match #0
    
    list_4 =   [t_id('d'), t_lbrace(), t_real(3.4), t_rbrace()]
    # d(3.4) - Should match #1
    
    transform_system = matcher ()
    transform_system.add_match (regexp_1)
    transform_system.enter_context ()
    transform_system.add_match (regexp_2)
    assert transform_system.match_stream (list_1) == (1, 4)
    transform_system.enter_context ()
    transform_system.add_match (regexp_3)
    assert transform_system.match_stream (list_2) == (2, 4)
    assert transform_system.match_stream (list_3) == (0, 5)
    transform_system.leave_context ()
    assert transform_system.match_stream (list_4) == (1, 4)


def test_case_1 ():
    """ A test for context switching and matching (depth = 1). """
    regexp_1 = [t_m_start(), t_id(), t_lbrace(), t_real(), t_m_asterisk(),
                t_rbrace(), t_m_end()]
    # {match} {id} '(' {real} * ')' {\match}

    list_1 =   [t_id('f'), t_lbrace(), t_real(3.5), t_rbrace()]
    # f(3.5) - Should match #0

    regexp_2 = [t_m_start(), t_id(), t_lbrace(), t_real(), t_rbrace(),
                t_m_end()]
    # {match} {id} '(' {real} ')' {\match}
    
    list_2 =   [t_id('g'), t_lbrace(), t_real(5.78), t_rbrace()]
    # g(5.78) - Should match #1

    list_3 =   [t_id('e'), t_lbrace(), t_real(4.0), t_real(5.8), t_rbrace()]
    # e(4.0 5.8) - Should match #0

    list_4 =   [t_id('d'), t_lbrace(), t_real(3.4), t_rbrace()]
    # d(3.4) - Should match #0

    transform_system = matcher ()
    transform_system.add_match (regexp_1)
    transform_system.enter_context ()
    assert transform_system.match_stream (list_1) == (0, 4)
    transform_system.add_match (regexp_2)
    assert transform_system.match_stream (list_2) == (1, 4)
    assert transform_system.match_stream (list_3) == (0, 5)
    transform_system.leave_context ()
    assert transform_system.match_stream (list_4) == (0, 4)


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

    transform_system = matcher ()
    transform_system.add_match (regexp_1)
    transform_system.add_match (regexp_2)
    transform_system.add_match (regexp_3)
    assert transform_system.match_stream (list_1) == (0, 3)
    assert transform_system.match_stream (list_2) == (1, 4)


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

    transform_system = matcher ()
    transform_system.add_match (regexp_1)
    transform_system.add_match (regexp_2)
    assert transform_system.match_stream (list_1) == (1, 3)
    assert transform_system.match_stream (list_2) == (0, 6)
    assert transform_system.match_stream (list_3) == (0, 4)


def test_case_4 ():
    """ A test for token types. """
    regexp_1 = [t_m_start(), t_m_lbrace(), t_real(), t_m_pipe(), t_int(),
                t_m_rbrace(), t_delim_col(), t_m_end()]
    # {match} ( {real} | {int} ) ';' {\match}

    regexp_2 = [t_m_start(), t_int(), t_delim_com(), t_m_end()]
    # {match} {int} ',' {\match}

    list_1 = [t_int(5), t_delim_col()]
    # 5; - Should match #0

    list_2 = [t_int(2), t_delim_com()]
    # 2, - Should match #1
    
    list_3 = [t_expr('4 + 13'), t_delim_col()]
    # 4 + 13; - Should not match

    transform_system = matcher ()
    transform_system.add_match (regexp_1)
    transform_system.add_match (regexp_2)
    assert transform_system.match_stream (list_1) == (0, 2)
    assert transform_system.match_stream (list_2) == (1, 2)
    assert transform_system.match_stream (list_3) is None


def test_case_5 ():
    """ A test for matching the longest sequence. """
    regexp_1 = [t_m_start(), t_m_lbrace(), t_real(), t_m_pipe(), t_int(),
                t_m_rbrace(), t_delim_com(), t_m_end()]
    # {match} ( {real} | {int} ) ',' {\match}
        
    regexp_2 = [t_m_start(), t_m_lbrace(), t_int(), t_delim_com(), t_m_rbrace(), 
                t_m_asterisk(), t_m_end()]
    # {match} ( {int} ',' ) * {\match}

    list_1 = [t_int(2), t_delim_com(), t_int(4), t_delim_com()]
    # 2, 4, - Should match #1

    list_2 = [t_int(2), t_delim_com(), t_int(4)]
    # 2, 4 - Should match #0, last symbol is lost

    transform_system = matcher ()
    transform_system.add_match (regexp_1)
    transform_system.add_match (regexp_2)
    assert transform_system.match_stream (list_1) == (1, 4)
    assert transform_system.match_stream (list_2) == (0, 2)


def test_case_6 ():
    """ A test for checking specific matching (with token values). """
    regexp_1 = [t_m_start(), t_id('foo'), t_m_end()]
    # {match} {id:foo} {\match}
    
    regexp_2 = [t_m_start(), t_id(), t_m_end()]
    # {match} {id} {\match}

    list_1 = [t_id()]
    # {id} - Should match #1
    
    list_2 = [t_id('foo')]
    # {id:foo} - Should match #0

    transform_system = matcher ()
    transform_system.add_match (regexp_1)
    transform_system.add_match (regexp_2)
    assert transform_system.match_stream (list_1) == (1, 1)
    assert transform_system.match_stream (list_2) == (0, 1)


def test_case_7 ():
    """ A test for checking specific matching (with token values) and the 
        longest match. """
    regexp_1 = [t_m_start(), t_id('foo'), t_int(), t_delim_col(), t_m_end()]
    # {match} {id:foo} {int} ';' {\match}
    
    regexp_2 = [t_m_start(), t_id(), t_int(), t_delim_col(),
                t_int(), t_m_asterisk(), t_m_end()]
    # {match} {id} {int} ';' {int} * {\match}
    
    list_1 = [t_id('foo'), t_int(4), t_delim_col()]
    # foo 4; - Should match #0

    list_2 = [t_id(), t_int(4), t_delim_col()]
    # {id} 4; - Should match #1

    list_3 = [t_id('foo'), t_int(4), t_delim_col(), t_int(5)]
    # foo 4; 5 - Should match #1

    transform_system = matcher ()
    transform_system.add_match (regexp_1)
    transform_system.add_match (regexp_2)
    assert transform_system.match_stream (list_1) == (0, 3)
    assert transform_system.match_stream (list_2) == (1, 3)
    assert transform_system.match_stream (list_3) == (1, 4)


def test_case_8 ():
    """ A test for checking contexts (are there any phantoms left after leaving
        a context). """
    regexp_1 = [t_m_start(), t_id(), t_m_end()]
    # {match} {id} {\match}

    regexp_2 = [t_m_start(), t_id(), t_m_asterisk(), t_m_end()]
    # {match} {id} {\match}
    
    list_1 = [t_id('foo'), t_id()]
    # foo - Should match #0
    
    list_2 = [t_id('bar'), t_id()]
    # bar - Should match #1
    
    transform_system = matcher ()
    transform_system.add_match (regexp_1)
    transform_system.enter_context ()
    transform_system.add_match (regexp_2)
    assert transform_system.match_stream (list_1) == (1, 2)
    transform_system.leave_context ()
    assert transform_system.match_stream (list_2) == (0, 1)


def test_case_9 ():
    """ A test for checking contexts (are there any phantoms left after leaving
        a context and entering another one). """
    regexp_1 = [t_m_start(), t_id(), t_m_end()]
    # {match} {id} {\match}
    
    regexp_2 = [t_m_start(), t_id(), t_m_asterisk(), t_m_end()]
    # {match} {id} {\match}
    
    list_1 = [t_id('foo'), t_id()]
    # foo - Should match #1
    
    list_2 = [t_id('bar'), t_id()]
    # bar - Should match #0

    transform_system = matcher ()
    transform_system.add_match (regexp_1)
    transform_system.enter_context ()
    transform_system.add_match (regexp_2)
    assert transform_system.match_stream (list_1) == (1, 2)
    transform_system.leave_context ()
    assert transform_system.match_stream (list_2) == (0, 1)
    transform_system.enter_context ()
    assert transform_system.match_stream (list_2) == (0, 1)
    transform_system.add_match (regexp_2)
    assert transform_system.match_stream (list_2) == (2, 2)


def test_case_10 ():
    """ A test for nothing to match. """
    list_1 = [t_id('foo'), t_id()]
    # foo - Should not match

    list_2 = [t_id('bar'), t_id()]
    # bar - Should not match

    transform_system = matcher ()
    transform_system.enter_context ()
    assert transform_system.match_stream (list_1) is None
    transform_system.leave_context ()
    assert transform_system.match_stream (list_2) is None


def execute_test (test_no):
    globals() ['test_case_' + str (test_no)]()


if __name__ == "__main__":
    for i in xrange (11):
        print
        print "================"
        print "Test case", i
        execute_test (i)
        print "================"

# vim: set ts=4 sw=4 sts=4 et