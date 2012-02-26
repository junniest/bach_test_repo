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
    
    def __repr__ (self):
        return "<abstract nfa node>"

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

    def __repr__ (self):
        return "{%s} char[%s]" % \
        ((self.num is not None and str(self.num) or ""), self.character)

class asterix_nfa (nfa):
    def __init__ (self, state):
        nfa.__init__ (self)
        self.content = state
        self.start = self
        self.end = self
        state.end.parent_asterix = self

    def __repr__ (self):
        return "{%s} (%s)*" %\
        ((self.num is not None and str(self.num) or ""), repr (self.content))

class or_nfa (nfa):
    def __init__ (self, state0, state1):
        nfa.__init__ (self)
        self.alternative = (state0, state1)
        self.start = self
        self.end = self
        state0.end.parent_or = self
        state1.end.parent_or = self
    
    def __repr__ (self):
        return "{%s} (%s | %s)" %\
        ((self.num is not None and str(self.num) or ""), \
          repr (self.alternative[0]), repr (self.alternative[1]))


class done_nfa (nfa):
    def __init__ (self):
        nfa.__init__ (self)
        self.start = self
        self.end = self

    def __repr__ (self):
        return "{%s} [done]" % \
        ((self.num is not None and str(self.num) or ""))

# Class for Determinate Finate Automaton
class node_dfa (object):
    "DFA node class"
    def __init__ (self, nfa_lst):
        num_lst = sorted ([str (s.num) for s in nfa_lst])
        self.id = ",".join (num_lst)
        self.states = nfa_lst
        self.paths = dict ()
        self.accepting = False
  
    def __repr__ (self):
        state_list = [repr (s) for s in self.states]
        return "<id:%s, accept:%r>" % (self.id, self.accepting)

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


def add_to_state_list (lst, dfa_lst):
    "Construct dfa from nfa states LST. In case dfa is not in\
     in the list -- add it.  Return dfa."
    dfa = node_dfa (lst)
    
    l = filter (lambda x: x.id == dfa.id, dfa_lst)
    if len (l) == 1:
        dfa = l[0];
    elif len (l) == 0:
        dfa_lst.append (dfa)
    else:
        raise Exception ("duplicate dfa with id %r found" % dfa.id)

    return dfa

def get_next_state(state):
    if state.nxt is not None:
        return state.nxt
    if state.parent_or is not None:
        return get_next_state(state.parent_or)

    # FIXME Looks really suspicious.  What if we have more than
    # two levels of nesting in asterix?
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
                moves.append (get_next_state(nfa_state))
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

def rearrange (dfa_state_list):
    for state in dfa_state_list:
        for nfa_state in state.states:
            if isinstance (nfa_state, done_nfa):
                state.accepting = True
    for i in xrange(len(dfa_state_list)):
        dfa_state_list[i].id = i
    return dfa_state_list

def det (automata, symbol_list):
    dfa_state_list = []
    nfa_state_list = get_epsilon_closure ([automata])
    
    if not nfa_state_list:
        raise Exception ("No states were found for %s" % automata)
        
    add_to_state_list (nfa_state_list, dfa_state_list)
    
    for dfa in dfa_state_list:
        for symbol in symbol_list:
            nl = get_epsilon_closure (get_moves (dfa, symbol))
            if nl:
               dfa.paths[symbol] = add_to_state_list (nl, dfa_state_list)
    
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
            # FIXME What the hell is this?
            # '.' means any symbool!
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


# vim: set ts=4 sw=4 sts=4 et
