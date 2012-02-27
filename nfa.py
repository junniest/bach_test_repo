__author__ = "Artem Shinkarov, June Pecherskaya"
__date__ = "2012-02-09"


# Abstract class for Nondeterminate Finite Automaton
class nfa (object):
    "NFA class for regular expressions"
    def __init__ (self):
        self.start = None
        self.end = None
        self.nxt  = None
        self.num = None
        self.parent = None

    def add_next_state (self, state):
        if self.start is None or self.end is None:
            raise Exception ("Abstract nfa instantiated")
        else:
            self.end.nxt = state.start
            self.end = state.end
        return self
    
    def __repr__ (self):
        return "<abstract nfa node>"


# Subclasses of NFA
class char_nfa (nfa):
    def __init__ (self, c):
        nfa.__init__ (self)
        self.character = c
        self.start = self
        self.end = self

    def __repr__ (self):
        str = "char[%s]" % (self.character) 
        if self.nxt is not None:
            str = str + " -> " + repr (self.nxt)
        return str

class asterix_nfa (nfa):
    def __init__ (self, state):
        nfa.__init__ (self)
        self.content = state
        self.start = self
        self.end = self
        state.end.parent = self

    def __repr__ (self):
        str = "( %s )*" % repr (self.content)
        if self.nxt is not None:
            str = str + " -> " + repr (self.nxt)
        return str


class or_nfa (nfa):
    def __init__ (self, state0, state1):
        nfa.__init__ (self)
        self.alternative = (state0, state1)
        self.start = self
        self.end = self
        state0.end.parent = self
        state1.end.parent = self
    
    def __repr__ (self):
        str = "( %s | %s )" % (repr (self.alternative[0]), repr (self.alternative[1]))
        if self.nxt is not None:
            str = str + " -> " + repr (self.nxt)
        return str


class done_nfa (nfa):
    def __init__ (self):
        nfa.__init__ (self)
        self.start = self
        self.end = self

    def __repr__ (self):
        if self.start.nxt is not None:
            raise Exception ("[Done] must be the last state of regexp")
        return "[Done]"


# Class for Determinate Finate Automaton
class node_dfa (object):
    "DFA node class"
    def __init__ (self, nfa_lst):
        self.states = nfa_lst
        self.paths = dict ()
        self.accepting = False
  
    def __repr__ (self):
        state_list = [repr (s) for s in self.states]
        return "<id:%s, accept:%r>" % (self.id, self.accepting)


def add_to_state_list (lst, dfa_lst):
    "Construct dfa from nfa states LST. In case dfa is not in\
     in the list -- add it.  Return dfa."
    dfa = node_dfa (lst)
    
    l = filter (lambda x: set (x.states) == set (dfa.states), dfa_lst)
    if len (l) == 1:
        dfa = l[0];
    elif len (l) == 0:
        dfa_lst.append (dfa)
    else:
        raise Exception ("duplicate dfa with id %r found" % dfa.states)

    return dfa


def get_next_state(state):
    if state.nxt is not None:
        return state.nxt
    if isinstance (state.parent, or_nfa):
        return get_next_state(state.parent)

    # FIXME Looks really suspicious.  What if we have more than
    # two levels of nesting in asterix?
    if isinstance (state.parent, asterix_nfa):
        if isinstance (state.parent.parent, asterix_nfa):
            return get_next_state(state.parent)
        else:
            return state.parent
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
        
        if isinstance (automata.parent, asterix_nfa):
            get_epsilon_closure_single (automata.parent, closure)


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

class getter (object):
    "Getter class for the string"
    def __init__ (self, string):
        self.string = string
        self.ind = 0

    def get_char (self):
        if self.ind < len(self.string):
            self.ind = self.ind + 1
            return self.string [self.ind - 1]
        else:
            return None
    
    def unget (self):
        self.ind = self.ind - 1
        
    def eof (self):
        if self.ind == len(self.string):
            return True
        return False

def concat (stack, seq_len):
    "If possible, concatenates the last seq_len states of the stack"
    i = 1
    while len (stack) > 1 and i < seq_len:
        state1 = stack.pop()
        state0 = stack.pop()
        stack.append (state0.add_next_state (state1))
        i = i + 1

def handle_primary (gtr, stack):
    "Handles the primary matches - characters and *, calls handle_or for brace content"
    c = gtr.get_char ();
    if c is None:
        return
    if c.isalnum ():
        stack.append (char_nfa (c))
        return
    if c == '*':
        stack.append (asterix_nfa (stack.pop ()))
        return
    if c == '(':
        handle_or (gtr, stack)
        c = gtr.get_char ()
        if c != ')':
            raise Exception ('Closing brace expected, got %s instead.' % c)
        return
    gtr.unget ()
    return

def handle_seq (gtr, stack):
    "Handles primary match sequenes"
    handle_primary (gtr, stack)
    seq_len = 1
    char = gtr.get_char ()
    while char is not None and char != '|' and char != ')':
        gtr.unget ()
        old_len = len (stack)
        handle_primary (gtr, stack)
        if (old_len != len (stack)):
            seq_len = seq_len + 1
        char = gtr.get_char ()
    concat (stack, seq_len)
    gtr.unget ()
    return

def handle_or (gtr, stack):
    "Handles or's"
    handle_seq (gtr, stack)
    if gtr.get_char () == "|":
        handle_seq (gtr, stack)
        state0 = stack.pop ()
        state1 = stack.pop ()
        stack.append (or_nfa (state1, state0))
    else:
        gtr.unget ()
    
def parse (string):
    gtr = getter (string)
    stack = []
    handle_or (gtr, stack)
    if not stack:
        raise Exception ('Empty regexp!')
    stack[0].add_next_state (done_nfa ())
    return stack[0]

# vim: set ts=4 sw=4 sts=4 et
