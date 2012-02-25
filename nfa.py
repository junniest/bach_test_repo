__author__ = "Artem Shinkarov, June Pecherskaya"
__date__ = "2012-02-09"

# Test commit, please ignore
# Abstract class for Nondeterminate Finite Automaton
class nfa (object):
    "NFA class for regular expressions"
    def __init__ (self):
        self.start = None
        self.end = None
        self.nxt  = None
        self.num = None
        self.parent_or = None
        self.parent_asterix = None

    def add_next_state (self, state):
        if self.start is None or self.end is None:
            raise Exception ("Abstract nfa instantiated")
        else:
            self.end.nxt = state.start
            self.end = state.end
        return self

    def xprint(self):
        if self.num is not None:
            print "{%i}" % self.num,
        if isinstance (self.start, char_nfa):
            print "char[%s]" % self.start.character,
        elif isinstance (self.start, asterix_nfa):
            print "(",
            self.start.content.xprint ()
            print ")*",
        elif isinstance (self.start, or_nfa):
            print "(",
            self.start.alternative[0].xprint ()
            print "|",
            self.start.alternative[1].xprint ()
            print ")",
        elif isinstance (self.start, done_nfa):
            print "[Done]"        
            if self.start.nxt is not None:
                raise Exception ("[Done] must be the last state of regexp")
        else:
            raise Exception ("unknown nfa class %s" % self.start.__classname__)
    
        if self.nxt is not None:
            print "->", 
            self.nxt.xprint ()

# Subclasses of NFA
class char_nfa (nfa):
    def __init__ (self, c):
        nfa.__init__ (self)
        self.character = c
        self.start = self
        self.end = self

class asterix_nfa (nfa):
  def __init__ (self, state):
    nfa.__init__ (self)
    self.content = state
    self.start = self
    self.end = self
    state.end.parent_asterix = self

class or_nfa (nfa):
    def __init__ (self, state0, state1):
        nfa.__init__ (self)
        self.alternative = (state0, state1)
        self.start = self
        self.end = self
        state0.end.parent_or = self
        state1.end.parent_or = self

class done_nfa (nfa):
    def __init__ (self):
        nfa.__init__ (self)
        self.start = self
        self.end = self

# Class for Determinate Finate Automaton
class node_dfa (object):
    "DFA node class"
    def __init__ (self, nfa_state_list):
        id = []
        for i in nfa_state_list:
            id.append(i.num)
        self.id = "".join([str(x) for x in sorted(id)])
        self.states = nfa_state_list
        self.paths = dict ()
        self.marked = False
        self.accepting = False
  
    def xprint (self):
        print self.id, " accepting: ", self.accepting 
        for symbol, state in self.paths.iteritems():
            if state:
                print symbol, state.id
            else:
                print symbol, None

def enumerate_states (automata, start=0):
    if automata is None:
        return start
    if automata.num is not None:
        return enumerate_states (automata.nxt, start)
    if isinstance (automata, char_nfa):
        automata.num = start
        start += 1
    elif isinstance (automata, asterix_nfa):
        automata.num = start
        start += 1
        start = enumerate_states (automata.content, start)
    elif isinstance (automata, or_nfa):
        automata.num = start
        start += 1
        start = enumerate_states (automata.alternative[0], start)
        start = enumerate_states (automata.alternative[1], start)
    elif isinstance (automata, done_nfa):
        automata.num = start
        start += 1
    return enumerate_states (automata.nxt, start)


def add_to_state_list (nfa_state_list, dfa_state_list):
    dfa_to_return = None
    new_dfa_state = node_dfa(nfa_state_list)
    for dfa_state in dfa_state_list:
        if dfa_state.id == new_dfa_state.id:
            dfa_to_return = dfa_state
            break
    if dfa_to_return is None:
        dfa_state_list.append(new_dfa_state)
        return new_dfa_state
    
    return dfa_to_return

def get_next_state(state):
    if state.nxt is not None:
        return state.nxt
    if state.parent_or is not None:
        return get_next_state(state.parent_or)
    if state.parent_asterix is not None:
        if state.parent_asterix.parent_asterix is not None:
            return get_next_state(state.parent_asterix)
        else:
            return state.parent_asterix
    return None

def get_moves (dfa_state, symbol):
    "Returns moves possible from the given dfa \
     state (nfa state list) by a specific symbol"
    moves = []
    for nfa_state in dfa_state.states:
        if isinstance (nfa_state, char_nfa):
            if nfa_state.character == symbol:
                moves.append(get_next_state(nfa_state))
    return moves

def get_epsilon_closure (nfa_state_list):
    "Epsilon closure for a list of states"
    closure = []
    closure_one = []
    
    for state in nfa_state_list:
        get_epsilon_closure_single (state, closure_one)
        if closure_one:
            closure = closure + closure_one
    if closure:
        return closure
    return None

def get_epsilon_closure_single (automata, closure):
    "Epsilon closure for a single state"
    if not automata is None and not automata in closure:
        if isinstance (automata, char_nfa) or isinstance (automata, done_nfa):
            closure.append (automata)
        elif isinstance (automata, asterix_nfa):
            closure.append (automata)
            get_epsilon_closure_single (automata.content, closure)
            get_epsilon_closure_single (get_next_state(automata), closure)
        elif isinstance (automata, or_nfa):
            closure.append (automata)
            get_epsilon_closure_single (automata.alternative[0], closure)
            get_epsilon_closure_single (automata.alternative[1], closure)
        
        if not automata.parent_asterix is None:
            get_epsilon_closure_single (automata.parent_asterix, closure)

def get_unmarked (dfa_state_list):
    "Gets first unmarked state from the dfa state list,\
     which means that it wasn't processed yet"
    new_list = filter(lambda x: not x.marked, dfa_state_list)
    if new_list:
        return new_list[0]
    return None

def get_state_to (nfa_state, dfa_state_list):
    "Returns a dfa state to which the given nfa path leads."
    if nfa_state.nxt is None:
        print "No next state"
        return None
    id = str (nfa_state.nxt.num)
    for dfa_state in dfa_state_list:
        # FIXME  What the hell is this?
        ind = -1
        try:
            ind = dfa_state.id.index(id)
        except:
            pass
        else:
            return dfa_state
    return None

def rearrange (dfa_state_list):
    for state in dfa_state_list:
        for nfa_state in state.states:
            if isinstance (nfa_state, done_nfa):
                state.accepting = True
    for i in xrange(len(dfa_state_list)):
        dfa_state_list[i].id = i
    return dfa_state_list

def determinate (automata, symbol_list):
    dfa_state_list = []
    nfa_state_list = get_epsilon_closure ([automata])
    
    if nfa_state_list:
        add_to_state_list (nfa_state_list, dfa_state_list)
        dfa_state = get_unmarked (dfa_state_list)
        while dfa_state:
            dfa_state.marked = True
            for symbol in symbol_list:
                new_nfa_state_list = get_epsilon_closure (get_moves (dfa_state, symbol))
                if new_nfa_state_list:
                   end_state = add_to_state_list (new_nfa_state_list, dfa_state_list)
                   dfa_state.paths[symbol] = end_state
            dfa_state = get_unmarked (dfa_state_list)
    
    return rearrange (dfa_state_list)

def parse_postfix (string, state_stack = [], num = 0):
    while num < len (string):
        char = string[num]
        if char == '(':
            num = num + 1
            num = parse_postfix (string, state_stack, num)
        elif char == ')':
            return num
        elif char == '*':
            content = state_stack.pop ()
            state = asterix_nfa (content)
            state_stack.append (state)
        elif char == '|':
            state1 = state_stack.pop ()
            state0 = state_stack.pop ()
            state = or_nfa (state0, state1)
            state_stack.append (state)
        elif char == '.':
            state1 = state_stack.pop ()
            state0 = state_stack.pop ()
            state0.add_next_state (state1)
            state_stack.append (state0)
        else:
            state = char_nfa (char)
            state_stack.append (state)
        num = num + 1
    state_stack[0].add_next_state(done_nfa())
    for i in state_stack:
        i.xprint ()
    return state_stack[0]

#parse_postfix ('(((vb.b.f)|)*(d)|)*')

# a(a|b)x*
#f = char_nfa ('a') \
#    .add_next_state (or_nfa (char_nfa ('a'), char_nfa ('b'))) \
#    .add_next_state (asterix_nfa (char_nfa ('x'))) \
#    .add_next_state (done_nfa ())
#postfix_string_f = 'a(ab|).x*.' 

# (a|b)*
#f = asterix_nfa(or_nfa(char_nfa('a'), char_nfa('b'))).add_next_state(done_nfa())
#postfix_string_f = '(ab|)*'

# (ab*|bb)
#f = or_nfa(char_nfa('a').add_next_state(asterix_nfa(char_nfa('b'))), char_nfa('b').add_next_state(char_nfa('b'))).add_next_state(done_nfa())
#postfix_string_f = 'ab*.bb.|'

#((c*)*)*
#f = asterix_nfa(asterix_nfa(asterix_nfa(char_nfa('c')))).add_next_state(done_nfa())
#postfix_string_f = 'c***'

#((c|a)|(b|xxb*))
#f = or_nfa(or_nfa(char_nfa('c'), char_nfa('a')), or_nfa(char_nfa('b'), char_nfa('x').add_next_state(char_nfa('x')).add_next_state(asterix_nfa(char_nfa('b'))))).add_next_state(done_nfa())
#postfix_string_f = '(ca|)(b(xx.b*.)|)|'

#(((a|b)|c)|x)
#f = or_nfa(or_nfa(or_nfa(char_nfa('a'), char_nfa('b')), char_nfa('c')), char_nfa('x')).add_next_state(done_nfa())
#postfix_string_f = 'cb|c|x|'

#x*(a|c)
f = asterix_nfa(char_nfa('x')).add_next_state(or_nfa(char_nfa('a'), char_nfa('c'))).add_next_state(done_nfa())
postfix_string_f = 'x*(ac|).' 

f.xprint ()

f = parse_postfix (postfix_string_f)
enumerate_states (f)

print

for i in determinate(f, 'abcxz'):
    if i is not None:
        print '------------------------'
        i.xprint ()

# vim: set ts=4 sw=4 sts=4 et
