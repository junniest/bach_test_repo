__author__ = "Artem Shinkarov, June Pecherskaya"
__date__ = "2012-02-09"

import collections
import time


""" ==== Nondeterminate Finite Automaton logic ==== """

""" ---- Abstract class for NFA ---- """

class nfa (object):
    """ NFA class for regular expressions. """
    def __init__ (self):
        self.start = None
        self.end = None
        self.nxt  = None
        self.num = None
        self.parent = None

    def add_next_state (self, state):
        """ Adds a next state. """
        if self.start is None or self.end is None:
            raise Exception ("Abstract nfa instantiated")
        else:
            self.end.nxt = state.start
            self.end = state.end
        return self

    def get_next_state(self):
        """ Returns the next state for an NFA state. """
        if self.nxt is not None:
            return self.nxt
        if isinstance (self.parent, or_nfa):
            return self.parent.get_next_state ()
        if isinstance (self.parent, asterisk_nfa):
            if isinstance (self.parent.parent, asterisk_nfa):
                return self.parent.get_next_state()
            else:
                return self.parent
        return None

    def __repr__ (self):
        return "<abstract nfa node>"


""" ---- Subclasses of NFA ---- """


class token_nfa (nfa):
    """ NFA class for matching a single token. """
    def __init__ (self, token):
        nfa.__init__ (self)
        self.token = token
        self.start = self
        self.end = self
    
    def get_epsilon_closure (self, closure):
        """ Epsilon closure for a single state. """
        if not self in closure:
            closure.add (self)
    
    def __repr__ (self):
        str = "%s" % (self.token) 
        if self.nxt is not None:
            str = str + " -> " + repr (self.nxt)
        return str


class asterisk_nfa (nfa):
    """ NFA class for matching an asterisk group. """
    def __init__ (self, state):
        nfa.__init__ (self)
        self.content = state
        self.start = self
        self.end = self
        state.end.parent = self

    def get_epsilon_closure (self, closure):
        """ Epsilon closure for a single state. """
        if not self in closure:
            closure.add (self)
            self.content.get_epsilon_closure (closure)
            self.get_next_state ().get_epsilon_closure (closure)
    
    def __repr__ (self):
        str = "( %s )*" % repr (self.content)
        if self.nxt is not None:
            str = str + " -> " + repr (self.nxt)
        return str


class or_nfa (nfa):
    """ NFA class for matching one of two alternatives. """
    def __init__ (self, state0, state1):
        nfa.__init__ (self)
        self.alternative = (state0, state1)
        self.start = self
        self.end = self
        state0.end.parent = self
        state1.end.parent = self

    def get_epsilon_closure (self, closure):
        """ Epsilon closure for a single state. """
        if not self in closure:
            closure.add (self)
            self.alternative[0].get_epsilon_closure (closure)
            self.alternative[1].get_epsilon_closure (closure)
    
    def __repr__ (self):
        str = "( %s | %s )" % (repr (self.alternative[0]), 
                               repr (self.alternative[1]))
        if self.nxt is not None:
            str = str + " -> " + repr (self.nxt)
        return str


class done_nfa (nfa):
    """ NFA class for the finishing state of the automaton """
    def __init__ (self):
        nfa.__init__ (self)
        self.start = self
        self.end = self

    def get_epsilon_closure (self, closure):
        """ Epsilon closure for a single state. """
        if not self in closure:
            closure.add (self)

    def __repr__ (self):
        if self.start.nxt is not None:
            raise Exception ("[Done] must be the last state of regexp")
        return "[Done]"


""" ==== Determinate Finite Automaton logic ==== """

class node_dfa (object):
    """ DFA node class. """
    def __init__ (self, nfa_lst):
        self.states = nfa_lst
        self.paths = {}
        self.accepting = False
        self.regexp_id = None
  
    def get_moves (self, token):
        """ Returns moves possible from the given DFA state (NFA state list)
            by a specific symbol. """
        moves = set()
        for nfa_state in self.states:
            if isinstance (nfa_state, token_nfa) and \
               token.eq(nfa_state.token):
                moves.add (nfa_state.get_next_state ())
        return moves
    
    def get_token_list (self):
        token_list = set ()
        for nfa_state in self.states:
            if isinstance (nfa_state, token_nfa):
                token_list.add(nfa_state.token)
        return token_list
    
    def __repr__ (self):
        state_list = map(lambda (x,y): str(x) + ' -> ' + repr(y.id), self.paths.iteritems())
        return "<id:%s, accept:%r>" % (self.id, self.accepting)#, state_list)

""" ---- Logic for DFA creation from an NFA ---- """

def add_to_state_list (nfa_lst, dfa_lst):
    """ Locate a DFA state in the list using the given the list of NFA states.
        If such a DFA state is present, return it. If it is not present, create
        a new state, add it to the DFA state list and return it. If two or more
        such states are present in the list - raise an exception. """
    dfa = None
    l = filter (lambda x: set (x.states) == set (nfa_lst), dfa_lst)
    if len (l) == 1:
        dfa = l[0]
    elif len (l) == 0:
        dfa = node_dfa (nfa_lst)
        dfa_lst.append (dfa)
    else:
        raise Exception ("Duplicate DFA state with id %r found" % dfa.states)
    return dfa


def get_epsilon_closure (nfa_state_list):
    """ Method gets the epsilon closure for a list of states. """
    closure = set()
    for state in nfa_state_list:
        state.get_epsilon_closure (closure)
    if closure:
        return closure
    return None


def rearrange (dfa_state_list):
    """ Method sets DFA state "accepting" parameter according to the NFA states 
        it contains. Then sets an id for the state and removes unnecessary 
        information (the list of NFA states). """
    for i in xrange(len(dfa_state_list)):
        dfa_state_list[i].accepting = \
            not not filter(lambda nfa_state: isinstance (nfa_state, done_nfa), 
                           dfa_state_list[i].states)
        dfa_state_list[i].id = i
        dfa_state_list[i].states = None
    return dfa_state_list


def det (automaton):
    """ Method creates a DFA for the given NFA using its starting state and a 
        list of symbols that are used in it for traversing the automaton. """
    dfa_state_list = []
    nfa_state_list = get_epsilon_closure ([automaton])
    if not nfa_state_list:
        raise Exception ("No states were found for %s" % automaton)

    add_to_state_list (nfa_state_list, dfa_state_list)
    
    for dfa in dfa_state_list:
        token_list = dfa.get_token_list ()
        for token in token_list:
            nl = get_epsilon_closure (dfa.get_moves (token))
            if nl:
               dfa.paths[token] = add_to_state_list (nl, dfa_state_list)
    return minimize (rearrange (dfa_state_list))


""" ---- Logic for DFA minimization ---- """

def get_group_no(state, group_list):
    """ Gets the group number which contains the state in question """
    for i in xrange (len (group_list)):
        if state in group_list[i]:
            return i
    raise Exception ("No group contains given state")


def break_to_groups (group, group_list):
    """ Breaks the given group into smaller groups according to the paths they 
        have. """
    result = []
    state_path_list = []
    # the cycle creates pairs of states and their paths encoded as paths to a 
    # particular group number in the given group_list
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
    """ This method minimizes the automata """
    # starting breakdown - accepting and not accepting states are separated into
    # two groups.
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
                new_group_list += break_to_groups(group[:], group_list)
        group_list = new_group_list
    return make_automata_from_groups (group_list)


def make_automata_from_groups (group_list):
    """ This method reforms a list of groups (after minimization) into an 
        automaton. """
    start_state = None
    # All the first elements of a group are a new state
    automaton = [group[0] for group in group_list]
    for group in group_list:
        new_state = group [0]
        if new_state.id == 0:
            start_state = new_state
        if len (group) == 1: 
            # if group length is 1 it's just a state, nothing to do
            continue
        # if s group has several states, we have to replace these states in all 
        # paths so that the paths are correct 
        for i in xrange(1, len (group)):
            old_state = group [i]
            if old_state.id == 0:
                start_state = new_state
            for state in automata:
                for (key, path) in state.paths.iteritems ():
                    if path == old_state:
                        state.paths[key] = new_state
    automaton.remove (start_state)
    automaton = sorted (automaton)
    automaton.insert (0, start_state)
    return automaton

""" ==== Regular expression parse logic on tokens ==== """

class getter (object):
    """ Token getter class for regular expression. """
    def __init__ (self, stream = None):
        self.stream = stream
        self.ind = 0
    
    def get_token (self):
        if self.ind < len(self.stream) and not isinstance(self.stream [self.ind], t_m_end):
            self.ind = self.ind + 1
            return self.stream [self.ind - 1]
        else:
            return None
    
    def unget (self):
        self.ind = self.ind - 1

class parser (object):
    """ Regular expression parser class. """
    def __init__ (self):
        self.gtr = None
        self.stack = None
    
    def concat (self, seq_len):
        """ If possible, concatenates the last seq_len states of the stack. """
        i = 1
        while len (self.stack) > 1 and i < seq_len:
            state1 = self.stack.pop()
            state0 = self.stack.pop()
            self.stack.append (state0.add_next_state (state1))
            i = i + 1
    
    def handle_primary (self):
        """ Handles the primary matches - characters and *, calls handle_or for
            brace content. """
        token = self.gtr.get_token ();
        if token is None:
            return
        if not isinstance (token, t_m_token):
            self.stack.append (token_nfa (token))
            return
        if isinstance (token, t_m_asterisk):
            self.stack.append (asterisk_nfa (self.stack.pop ()))
            return
        if isinstance (token, t_m_lbrace):
            self.handle_or ()
            token = self.gtr.get_token ()
            if not isinstance (token, t_m_rbrace):
                raise Exception ('Closing brace expected, got %s instead.' % token)
            return
        self.gtr.unget ()
        return
    
    def handle_seq (self):
        """ Handles primary match sequenes. """
        self.handle_primary ()
        seq_len = 1
        token = self.gtr.get_token ()
        while token is not None and not isinstance (token, t_m_pipe) \
            and not isinstance (token, t_m_rbrace):
                self.gtr.unget ()
                old_len = len (self.stack)
                self.handle_primary ()
                if (old_len != len (self.stack)):
                    seq_len = seq_len + 1
                token = self.gtr.get_token ()
        self.concat (seq_len)
        self.gtr.unget ()
        return
    
    def handle_or (self):
        """ Handles or's. """
        self.handle_seq ()
        if isinstance (self.gtr.get_token (), t_m_pipe):
            self.handle_seq ()
            state0 = self.stack.pop ()
            state1 = self.stack.pop ()
            self.stack.append (or_nfa (state1, state0))
        else:
            self.gtr.unget ()
    
    def parse (self, regexp):
        """ Parses the giver regular expression and creates an NFA. """
        self.gtr = getter (regexp)
        self.stack = []
        self.handle_or ()
        if not self.stack:
            raise Exception ('Empty regexp!')
        self.stack[0].add_next_state (done_nfa ())
        return self.stack[0]


""" ==== DFA merge logic ==== """

class node_dfa_m (object):
    """ Merged DFA node class. """
    def __init__ (self, state_list):
        self.paths = {}
        if isinstance(state_list[0], node_dfa_m):
            new_list = state_list[0].state_list
            new_list.append(state_list[1])
            self.state_list = new_list
        elif state_list[0] is None:
            self.state_list = [state_list[1]]
        else:
            self.state_list = state_list
        self.accepting_id_list = []
    
    def __repr__ (self):
        state_list = map(lambda (x,y): str(x) + ' -> ' + repr(y.state_list),
                         self.paths.iteritems())
        return "State %r %r" % (self.state_list, state_list)
        pass


def add_to_state_list_m (dfa_state_list, merge_dfa_state_list):
    """ Locate a merged DFA state in the list using the given the list of
        unmerged DFA states. If such a state is present, return it. If it is not
        present, create a new state, add it to the state list and return it. If
        two or more such states are present in the list - raise an 
        exception. """
    state = None
    l = filter (lambda x: x.state_list == dfa_state_list, merge_dfa_state_list)
    if len (l) == 1:
        state = l[0]
    elif len (l) == 0:
        state = node_dfa_m (dfa_state_list)
        merge_dfa_state_list.append (state)
    else:
        raise Exception ("Duplicate state found during merge")
    return state


def merge_paths (merge_list):
    """ For a list of states from unmerged DFA creates a dictionary with paths
        by a symbol to different lists of states. """
    rv = collections.defaultdict(list)
    for merge in merge_list:
        for k, v in merge.paths.iteritems():
            rv[k].append(v)
    return rv


def merge (automata_list):
    """ Merges a list of automata into a single one to improve execution 
        time. """
    merge0 = [None]
    for merge1 in automata_list[0:]:
        first_state = node_dfa_m([merge0[0], merge1[0]])
        new_automata = [first_state]
        for state in new_automata:
            rv = merge_paths(state.state_list)
            for (symbol, state_list) in rv.iteritems():
                state.paths[symbol] = add_to_state_list_m (state_list, 
                                                           new_automata)
        merge0 = new_automata
    return new_automata


""" ==== Merged DFA execution logic ==== """

def execute (token_list, regexp_list):
    """ Methods parses the given regular expressions, then creates a single DFA
        from all of the expressions and matches the given string with the 
        created DFA. """
    start_time = time.time()
    prs = parser ()
    automata_list = [det(prs.parse(x)) for x in regexp_list]
    for i in xrange (len (automata_list)):
        for state in automata_list[i]:
            state.regexp_id = i
    automata = merge (automata_list)
    current_state = automata[0]
    fail = False
    for token in token_list:
        l = filter (lambda (x, y): x.eq(token),
                    current_state.paths.iteritems ())
        if l:
            current_state = l[0][1]
        else:
            fail = True
            break
    if fail:
        return (None, automata, time.time() - start_time)
    else:
        accepted = filter(lambda x: x.accepting, current_state.state_list)
        if not accepted:
            return (None, automata, time.time() - start_time)
        else:
            return (accepted[0].regexp_id, automata, time.time() - start_time)


""" ==== Test token classes === """

class t_token (object):
    def __init__ (self, value = None):
        self.value = value

    def __repr__ (self):
        if self.value is not None:
            return "[" + self.__class__.__name__[2:] + ":" + str(self.value) + "]"
        else:
            return "[" + self.__class__.__name__[2:] + "]"

    def eq (self, token):
        if isinstance(token, self.__class__):
            if self.value is None:
                return True
            elif self.value == token.value:
                return True
        return False

class t_id (t_token):
    pass

class t_expr (t_token):
    pass

class t_real (t_expr):
    pass

class t_int (t_real):
    pass

class t_short (t_int):
    pass

class t_bool (t_short):
    def __init__ (self, value = None):
        if value:
            self.value = True
        else:
            self.value = False

class t_context_start (t_token):
    def __repr__ (self):
        return "[{]"

class t_context_end (t_token):
    def __repr__ (self):
        return "[}]"

class t_delim_col (t_token):
    def __repr__ (self):
        return "[;]"

class t_delim_com (t_token):
    def __repr__ (self):
        return "[,]"

class t_lbrace (t_token):
    def __repr__ (self):
        return "[(]"

class t_rbrace (t_token):
    def __repr__ (self):
        return "[)]"

""" Match tokens """

class t_m_token (t_token):
    def __repr__ (self):
        return ""

class t_m_lbrace (t_m_token):
    def __repr__ (self):
        return "("

class t_m_rbrace (t_m_token):
    def __repr__ (self):
        return ")"

class t_m_asterisk (t_m_token):
    def __repr__ (self):
        return "*"

class t_m_pipe (t_m_token):
    def __repr__ (self):
        return "*"

class t_m_start (t_m_token):
    def __repr__ (self):
        return "[match]"

class t_m_end (t_m_token):
    def __repr__ (self):
        return "[\match]"


# vim: set ts=4 sw=4 sts=4 et
