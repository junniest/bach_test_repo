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
        self.paths = {}
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
    
    return minimize (rearrange (dfa_state_list))


def get_group_no(state, group_list):
    "Gets the group number which contains the state in question"
    for i in xrange (len (group_list)):
        if state in group_list[i]:
            return i
    raise Exception ("No group contains given state")


def break_to_groups (group, group_list):
    "Breaks the given group into smaller groups according to the paths they have"
    result = []
    state_path_list = []
    # the cycle creates pairs of states and their paths encoded as paths to a particular group number in the given group_list
    for state in group:
        paths = {}
        for char, path in state.paths.iteritems ():
            paths[char] = get_group_no(state.paths.get (char), group_list)
        state_path_list.append ((state, paths))
    # split the created list into smaller groups according to their paths
    while state_path_list:
        state, paths = state_path_list.pop ()
        new_group = [state]
        remaining_state_path_list = []
        for nstate, npaths in state_path_list:
            if npaths == paths:
                new_group.append (nstate)
            else:
                remaining_state_path_list.append ((nstate, npaths))
        state_path_list = remaining_state_path_list
        result.append (sorted (new_group))
    return result


def minimize (automata):
    "This method minimizes the automata"
    # starting breakdown - finishing and unfinishing states are separated
    group_list = [[],[]]
    for state in automata:
        if state.accepting:
            group_list[0].append (state)
        else:
            group_list[1].append (state)
    old_group_list = []
    
    # if old and new group lists are equal, we're done minimizing
    while not group_list == old_group_list:
        old_group_list = group_list[:]
        new_group_list = []
        for group in group_list:
            if len(group) == 1:
                new_group_list.append(group)
            else:
                new_group_list = new_group_list + break_to_groups(group[:], group_list)
        group_list = new_group_list
    return make_automata_from_groups (group_list)


def make_automata_from_groups (group_list):
    "This method reforms a list of groups (after minimization) into an automata"
    start_state = None
    # All the first elements of a group are a new state
    automata = [group[0] for group in group_list]
    for group in group_list:
        if len (group) == 1: # if group length is 1 it's just a state, nothing to do
            break
        # if s group has several states, we have to replace these states in all paths so that the paths are correct 
        new_state = group [0]
        for i in xrange(2, len (group)):
            old_state = group [i]
            for state in automata:
                for (key, path) in state.paths.iteritems ():
                    if path.equals (old_state):
                        state.paths[key] = new_state
                        break
    for state in automata:
        if state.id == 0:
            start_state = state
            break
    automata.remove (start_state)
    automata = sorted (automata)
    automata.insert (0, start_state)
    return automata

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

def execute (string, automata_list, regexp_list):
    auto_dict = dict (zip (xrange (len(automata_list)), [auto[0] for auto in automata_list]))
    for char in string:
        to_throw_out = []
        for key in auto_dict.iterkeys ():
            if auto_dict.get (key).paths.has_key (char):
                auto_dict[key] = auto_dict.get (key).paths.get (char)
            else:
                to_throw_out.append (key)
        auto_dict = dict (filter (lambda (key, item): not key in to_throw_out, auto_dict.iteritems()))
    auto_dict = dict (filter (lambda (key, item): item.accepting, auto_dict.iteritems()))
    
    for i in auto_dict.iterkeys ():
        print "Accepted regexp ", regexp_list [i]
    if not auto_dict:
        print "No accepted regexps"

# vim: set ts=4 sw=4 sts=4 et
