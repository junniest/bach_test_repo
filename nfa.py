__author__ = "Artem Shinkarov, June Pecherskaya"
__date__ = "2012-02-09"

import collections
import time
from ordered_default_dict import DefaultOrderedDict


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
        assert None not in (self.start, self.end), "Abstract nfa instantiated"
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
        if self not in closure:
            closure.add (self)

    def __repr__ (self):
        str = "%s" % (self.token)
        if self.nxt is not None:
            str += " -> " + repr (self.nxt)
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
            str += " -> " + repr (self.nxt)
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
        if self not in closure:
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
        if self not in closure:
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
        self.id = None

    def get_moves (self, token):
        """ Returns moves possible from the given DFA state (NFA state list)
            by a specific symbol. """
        return set (s.get_next_state () for s in self.states
                    if isinstance (s, token_nfa) and token.le (s.token))

    def get_tokens (self):
        return set (s.token for s in self.states if isinstance(s, token_nfa))

    def set_regexp_id (self, regexp_id):
        self.regexp_id = regexp_id

    def __repr__ (self):
        state_list = map (lambda (x,y): str(x) + ' -> ' + repr(y.id), self.paths.iteritems())
        return "<id:%s, regexp_id:%s, accept:%r>" % (self.id, self.regexp_id, 
                                                     self.accepting)#, state_list)

""" ---- Logic for DFA creation from an NFA ---- """

def add_to_state_list (nfa_lst, dfa_lst):
    """ Locate a DFA state in the list using the given the list of NFA states.
        If such a DFA state is present, return it. If it is not present, create
        a new state, add it to the DFA state list and return it. If two or more
        such states are present in the list - raise an exception. """
    dfa = None
    nfa_set = set (nfa_lst)
    l = filter (lambda x: set (x.states) == nfa_set, dfa_lst)
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
    return closure or None


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


def det (automaton, regexp_id):
    """ Method creates a DFA for the given NFA using its starting state and a
        list of symbols that are used in it for traversing the automaton. """
    nfa_state_list = get_epsilon_closure ([automaton])
    if not nfa_state_list:
        raise Exception ("No states were found for %s" % automaton)
    dfa_state_list = []

    add_to_state_list (nfa_state_list, dfa_state_list)

    for dfa in dfa_state_list:
        dfa.set_regexp_id (regexp_id)
        for token in dfa.get_tokens ():
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

    while True:
        new_group_list = []
        for group in group_list:
            if len(group) == 1:
                new_group_list.append(group)
            else:
                new_group_list += break_to_groups(group, group_list)
        if group_list == new_group_list:
            return make_automata_from_groups (group_list)
        group_list = new_group_list


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
                for key, path in state.paths.iteritems ():
                    if path == old_state:
                        state.paths[key] = new_state
    automaton.remove (start_state)
    automaton.sort ()
    automaton.insert (0, start_state)
    return automaton

""" ==== Regular expression parse logic on tokens ==== """

class getter (object):
    """ Token getter class for regular expression. """
    def __init__ (self, stream = None):
        self.stream = stream
        self.ind = 0

    def get_token (self):
        if self.ind < len(self.stream):
            self.ind += 1
            return self.stream [self.ind - 1]
        else:
            return None

    def unget (self):
        self.ind -= 1

class regexp_parser (object):
    """ Regular expression parser class. """
    def __init__ (self, gtr = None):
        self.gtr = gtr
        self.stack = None

    def concat (self, seq_len):
        """ If possible, concatenates the last seq_len states of the stack. """
        i = 1
        while len (self.stack) > 1 and i < seq_len:
            state1 = self.stack.pop()
            state0 = self.stack.pop()
            self.stack.append (state0.add_next_state (state1))
            i += 1

    def handle_primary (self):
        """ Handles the primary matches - characters and *, calls handle_or for
            brace content. """
        token = self.gtr.get_token ();
        if token is None:
            return
        if not isinstance (token, t_m_token):
            # We've got some hacks coming up (this replaces token type
            # inheritance, as it messes up the matching process)
            if isinstance (token, t_expr):
                self.stack.append (or_nfa (or_nfa (token_nfa (t_expr ()), 
                                                   token_nfa (t_real ())),
                                           or_nfa (token_nfa (t_int ()), 
                                                   token_nfa (t_bool ()))))
            elif isinstance (token, t_real):
                self.stack.append (or_nfa (or_nfa (token_nfa (t_real()),
                                                   token_nfa (t_int())),
                                           token_nfa (t_bool ())))
            elif isinstance (token, t_int):
                self.stack.append (or_nfa (token_nfa (t_int()),
                                           token_nfa (t_bool ())))
            else:
                self.stack.append (token_nfa (token))
            return
        if isinstance (token, t_m_asterisk):
            self.stack.append (asterisk_nfa (self.stack.pop ()))
            return
        if isinstance (token, t_m_lbrace):
            self.handle_or ()
            token = self.gtr.get_token ()
            if not isinstance (token, t_m_rbrace):
                raise Exception ("Closing brace expected, got %s instead." % token)
            return
        self.gtr.unget ()

    def handle_seq (self):
        """ Handles primary match sequenes. """
        self.handle_primary ()
        seq_len = 1
        token = self.gtr.get_token ()
        while token is not None and not \
                isinstance (token, (t_m_pipe, t_m_rbrace, t_m_end)):
            self.gtr.unget ()
            old_len = len (self.stack)
            self.handle_primary ()
            if (old_len != len (self.stack)):
                seq_len = seq_len + 1
            token = self.gtr.get_token ()
        self.concat (seq_len)
        self.gtr.unget ()

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

    def parse (self, regexp_id):
        """ Parses the giver regular expression and creates an NFA. """
        self.stack = []
        self.handle_or ()
        if not self.stack:
            raise Exception ('Empty regexp!')
        self.stack[0].add_next_state (done_nfa ())
        return det (self.stack[0], regexp_id)


""" ==== DFA merge logic ==== """

class node_dfa_m (object):
    """ Merged DFA node class. """
    def __init__ (self, level, merged_state, single_state):
        """ The object is created with 2 states, a previous merged automaton
            state and the newly added (if such exists) state. This is done to
            make path merging easier (no need to recalculate paths for each 
            single dfa state, but only for 2 existing states). """
        self.paths = DefaultOrderedDict (list)
        self.state_list = contexted_state_list ()
        self.level = level
        self.merged_state = merged_state
        self.single_state = single_state

    def get_accepting(self):
        """ Gets the first accepting state in the dfa state list. """
        return self.state_list.get_accepting ()

    def rearrange (self):
        """ The method merges the states together in a single list. """
        if self.merged_state is not None:
            self.state_list = self.merged_state.state_list.copy ()
        if self.single_state is not None:
            self.state_list.add (self.level, self.single_state)
        return self

    def __repr__ (self):
        state_list = map(lambda (x,y): str(x) + ' -> ' + repr(y.state_list),
                         self.paths.iteritems())
        return "State %r %r" % (self.state_list, state_list)


def add_to_state_list_m (level, dfa_state_list, merge_dfa_state_list):
    """ Locate a merged DFA state in the list using the given the list of
        unmerged DFA states. If such a state is present, return it. If it is not
        present, create a new state, add it to the state list and return it. If
        two or more such states are present in the list - raise an
        exception. """
    state = None
    merged_state = single_state = None
    for i in dfa_state_list:
        if isinstance (i, node_dfa_m):
            merged_state = i
        elif isinstance (i, node_dfa):
            single_state = i
    
    l = filter (lambda x: x.merged_state == merged_state and 
                x.single_state == single_state, merge_dfa_state_list)
    if len (l) == 1:
        state = l[0]
    elif len (l) == 0:
        state = node_dfa_m (level, merged_state, single_state)
        merge_dfa_state_list.append (state)
    else:
        raise Exception ("Duplicate state found during merge")
    return state


def merge_paths (state):
    """ For a list of states from unmerged DFA creates a dictionary with paths
        by a symbol to different lists of states. """
    rv = DefaultOrderedDict (list)
    for merge in [state.merged_state, state.single_state]:
        if merge is None:
            continue
        for k, v in merge.paths.iteritems ():
            rv[k].append (v)
    return rv


def rearrange_m (new_automata):
    """ Calls rearrange for all of the new states. """
    return [state.rearrange () for state in new_automata]


def merge (level, merge_state_0, merge_state_1):
    """ Merges a list of automata into a single one to improve execution
        time. """
    first_state = node_dfa_m(level, merge_state_0, merge_state_1)
    new_automata = [first_state]
    for state in new_automata:
        rv = merge_paths (state)
        for (symbol, state_list) in rv.iteritems():
            state.paths[symbol] = add_to_state_list_m (level, state_list,
                                                       new_automata)
    return rearrange_m (new_automata)


""" ==== Test token classes === """

class t_token (object):
    """ Default token """
    repr_s = None

    def __init__ (self, value = None):
        self.value = value

    def __repr__ (self):
        if self.repr_s:
            return self.repr_s
        elif self.value is None:
            return "[" + type(self).__name__[2:] + "]"
        else:
            return "[" + type(self).__name__[2:] + ":" + str(self.value) + "]"

    def le (self, token):
        assert type(token) != type
        return isinstance(token, type(self)) and (self.value is None or
                                                  self.value == token.value)

    def __hash__ (self):
        return hash((type(self), self.value))
    
    def __eq__ (self, other):
        return type(self) == type(other) and self.value == other.value

""" ---- Specific tokens ---- """

class t_id (t_token):
    pass

class t_expr (t_token):
    pass

class t_real (t_token):
    pass

class t_int (t_token):
    pass

class t_bool (t_token):
    def __init__ (self, value = None):
        if value is None:
            self.value = None
        else:
            if value:
                self.value = True
            else:
                self.value = False

class t_context_start (t_token):
    repr_s = "[{]"

class t_context_end (t_token):
    repr_s = "[}]"

class t_delim_col (t_token):
    repr_s = "[;]"

class t_delim_com (t_token):
    repr_s = "[,]"

class t_lbrace (t_token):
    repr_s = "[(]"

class t_rbrace (t_token):
    repr_s = "[)]"

class t_oper (t_token):
    pass

""" Match tokens """

class t_m_token (t_token):
    repr_s = ""

class t_m_lbrace (t_m_token):
    repr_s = "("

class t_m_rbrace (t_m_token):
    repr_s = ")"

class t_m_asterisk (t_m_token):
    repr_s = "*"

class t_m_pipe (t_m_token):
    repr_s = "|"

class t_m_start (t_m_token):
    repr_s = "[match]"

class t_m_end (t_m_token):
    repr_s = "[\match]"

""" ==== Execution logic ==== """

def execute (stream):
    """ Parses a stream of tokens. Creates automata when encounters a regular
        expression. """
    get = getter (stream)
    token = get.get_token ()
    r_prs = regexp_parser (get)
    regexp_id = 0
    automaton = None
    current_state_list = []
    current_level = 0
    automata_stack = []
    while token is not None:
        if isinstance (token, t_m_start):
            auto = r_prs.parse (regexp_id)
            regexp_id += 1
            if automaton is None:
                automaton = merge (current_level, None, auto[0])
            else:
                automaton = merge (current_level, automaton[0], auto[0])
            print "Added a regexp, level", current_level, ", id", \
                   auto[0].regexp_id 
        elif isinstance (token, t_context_start):
            automata_stack.append (automaton)
            current_level += 1
            print "Entered a context, level", current_level
        elif isinstance (token, t_context_end):
            automaton = automata_stack.pop ()
            current_level -= 1
            print "Left a context, level", current_level
        else:
            if automaton is not None:
                current_state_list.append((automaton [0], []))
            new_state_list = []
            for state, processed_token_list in current_state_list:
                moves = filter (lambda (x, y): x.le (token),
                            state.paths.iteritems ())
                if moves:
                    processed_token_list.append (token)
                    new_state = moves[0][1]
                    i = new_state.get_accepting()
                    if i is None:
                        new_state_list.append((new_state, processed_token_list))
                    else:
                        print "\tAccepted regexp", i, processed_token_list
            current_state_list = new_state_list
        token = get.get_token ()


""" ==== States grouped by contexts ==== """

class contexted_state_list(object):
    """
        >>> n1 = node_dfa([]); n1.regexp_id = 1
        >>> n2 = node_dfa([]); n2.regexp_id = 2
        >>> n3 = node_dfa([]); n3.regexp_id = 3
        >>> n4 = node_dfa([]); n4.regexp_id = 4
        >>> n5 = node_dfa([]); n5.regexp_id = 5
        >>> l = contexted_state_list()
        >>> l.add(0, n1)
        >>> l.add(0, n2)
        >>> l.add(1, n3)
        >>> l.add(1, n4)
        >>> l.add(2, n5)
        >>> [node.state.regexp_id for node in l.list]
        [2, 1, 4, 3, 5]
        """

    def __init__(self):
        self.list = []
        self.last_level = None
        self.idx = None

    def copy (self):
        rv = type (self) ()
        rv.list = self.list[:]
        rv.last_level = self.last_level
        rv.idx = self.idx
        return rv

    def add (self, level, state):
        if self.last_level != level:
            self.last_level = level
            self.idx = -1
            self.list.append(state)
        else:
            self.list.insert(self.idx, state)
            self.idx -= 1

    def get_accepting (self):
        for state in self.list[::-1]:
            if state.accepting:
                return state.regexp_id
        return None
    
    def __repr__ (self):
        return repr (self.list)

# vim: set ts=4 sw=4 sts=4 et
