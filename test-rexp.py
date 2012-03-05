import random
import re
import nfa


def random_symbol ():
    return chr (ord ('a') + random.randint (0, 25))

def random_word (l):
    s = ""
    for _ in xrange (l):
        s += random_symbol ()
    return s

def random_group (s, rec):
    if (rec == 0):
        return s

    if (s == ""):
        s = random_word (random.randint (1, 5));

    g = random.randint (1, 3);
    if (g == 1):
        return random_group (s, rec-1)
    elif (g == 2):
        return "(%s)*" % random_group (s, rec-1)
    elif (g == 3):
        s = random_group (s, rec-1)
        s1 = random_group ("", rec)
        return "(%s|%s)" % (s, s1)

def random_rexp ():
    return random_group ("", 4)


def gen_test ():
    s =  random_rexp ()
    r = None
    try:
        r = re.compile (s)
    except Exception as inst:
        # Stupid python dose not like some of
        # random regexps.  :(
        pass

    ss = []
    for t in s:
        if t >= 'a' and t <= 'z':
            ss += t
    ns = ""
    for p in xrange (len (ss) * 3):
        ns += ss[random.randint (0, len (ss) -1)]

    return s, ns, r


def test_nfa_rexp ():
    import nfa

    rexp, string, matcher = gen_test ()
    print rexp, string

    if (matcher is None):
        print "Syupid python cannot build a matcher for %s" % rexp
    else:
        print  matcher.match(string)

    letters = "".join ([chr (ord ('a') + c) for c in xrange (26)])

    # FIXME This thing loops forever by some reason
    res = nfa.execute (string, [nfa.det (nfa.parse (rexp), letters)], [rexp])     

    # further here we should have something like
    # res_nfa = matcher.match (string)
    # if res_nfa is not None and res is not None
    #   print "test passed"
    # elif res_nfa is None and res is None
    #   print "test passed"
    # else:
    #   print "test failed"

test_nfa_rexp ()

