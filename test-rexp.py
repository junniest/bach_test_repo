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

def random_group (s, rec, ms):
    if (rec == 0):
        return s, ms

    if s == "":
        s = random_word (random.randint (1, 5));

    if ms == "":
	ms = s

    g = random.randint (1, 3);
    if (g == 1):
        return random_group (s, rec-1, ms)
    elif (g == 2):
	s, ms = random_group (s, rec-1, ms)
	w = random_word (random.randint (1,5))

        return "((%s)*%s)" % (s, w), (ms * random.randint (0,3)) + w
    elif (g == 3):
        s, ms1 = random_group (s, rec-1, ms)
        s1, ms2 = random_group ("", rec, "")

	if random.randint (1,2) == 1:
	  ms = ms1
	else: 
	  ms = ms2
        return "(%s|%s)" % (s, s1), ms

def random_rexp ():
    rexp, ms = random_group ("", 4, "")
    return "(%s)" % rexp, ms


def gen_test ():
    s, ms =  random_rexp ()
    r = None
    try:
        r = re.compile ('^'+s+'$')
    except Exception as inst:
        # Stupid python dose not like some of
        # random regexps.  :(
        pass

    return s, ms, r


def test_nfa_rexp (num):
    import nfa

    rexp, string, matcher = gen_test ()

    # print "matching `%s' against `%s'" % (rexp, string)
    
    pytest = False
    if matcher is not None:
	m = matcher.match (string)
	if m is not None:
	    pytest = m.group (0) == string

    res = nfa.execute (string, [rexp])
    #print "\tpython:%r\t\tpechka-nfa:%r" % (pytest, res)
    if pytest == res:
	print "Test %i: passed!" % num
    else:
	print "Test %i: failed!" % num
	print "\t`%s' against `%s'" % (rexp, string)
	print "\tpython:%r\t\tpechka-nfa:%r" % (pytest, res)

for i in xrange (500):
    test_nfa_rexp (i+1)
