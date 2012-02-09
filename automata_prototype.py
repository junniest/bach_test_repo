def move(state, symbol):
    for (path, nstate) in state.paths:
        if path == symbol:
            return nstate
    return None

def imitate_automata(automata, string):
    state = 0
    cur_len = 0
    for char in string:
        state = move(automata[state], char)
        cur_len = cur_len + 1
        print state, char
        if state is None:
            print "Oh noes, a dead end"
            return False
        else:
            if automata[state].accept and cur_len == len(string):
                print "we got accept"
                return True
    print "no accept ):"
    return automata[state].accept

###################################

# An automata node
class node:
    def __init__(self, id, paths, accept):
        self.id = id
        self.paths = paths
        self.accept = accept
        self.marked = False

    def __repr__(self):
        return "\nMe " + str(self.id)  + "  accept " + str(self.accept) + "\npaths " + str(self.paths) 

########################################

# Returns the moves available by an epsilon from a single state
def get_epsilon_paths(state):
    paths = [state.id]
    for (path, nstate) in state.paths:
        if path is None:
            paths.append(nstate)
    return list(set(paths))

# Returns the moves available by a symbol from a single state
def get_symbol_paths(state, symbol):
    paths = []
    for (path, nstate) in state.paths:
        if path == symbol:
            paths.append(nstate)
    return list(set(paths))

# Returns the moves possible by a symbol from a list of states
def get_moves(state, state_list, symbol):
    state_nums_undone = state.id[:]
    new_states = []
    while len(state_nums_undone) > 0:
        s = state_nums_undone.pop()
        tmp_states = get_symbol_paths(state_list[s], symbol)
        for tmp in tmp_states:
            if not tmp in new_states:
                new_states.append(tmp)
                state_nums_undone.append(tmp)
    return new_states 

# Returns the epsilon closure of a state list
def get_epsilon_closure(state_nums, automata):
    state_nums_undone = state_nums[:]
    new_states = state_nums[:]
    while len(state_nums_undone) > 0:
        s = state_nums_undone.pop()
        tmp_states = get_epsilon_paths(automata[s])
        for tmp in tmp_states:
            if not tmp in new_states:
                new_states.append(tmp)
                state_nums_undone.append(tmp)
    return new_states 

# Returns the id of the first unmarked state in the list
def get_unmarked(states):
    for i in xrange(len(states)):
        if not states[i].marked:
            return i
    return None

# Checks if a state already exists in a list
def check_if_in(state, state_list):
    for lstate in state_list:
        if lstate.id == state:
            return True
    return False

# Checks if a combination of automata states makes an accepting state or not
def is_an_accept_state(state_list, automata):
    return reduce(lambda x, y: x or y.accept, [automata[i] for i in state_list], False)

# determinates the automata that is given
def determinate_automata(undmoves, symbol_list):
    dstates = [node(sorted(get_epsilon_closure([0], undmoves)), [], False)]
    no = get_unmarked(dstates)
    while no is not None:
        dstates[no].marked = True
        for symbol in symbol_list:
            state_code = sorted(get_epsilon_closure(get_moves(dstates[no], undmoves, symbol), undmoves))
            if state_code:
                if not check_if_in(state_code, dstates):
                    dstates.append(node(state_code, [], is_an_accept_state(state_code, undmoves)))
                dstates[no].paths.append((symbol, state_code))
        no = get_unmarked(dstates)
    return transform_to_nodes(dstates)

aut2 = [node(0, [('1', 1), (None, 1)], False), node(1, [('2', 1), ('1', 2), ('1', 1), (None, 2)], False), node(2, [], True)]

# Transforms the the nodes with state lists as ids to nodes with single number ids
def transform_to_nodes(weird_auto):
    dict = [r.id for r in weird_auto]
    new_auto = []
    for state in weird_auto:
        new_paths = []
        map(lambda (symbol, new_state): new_paths.append((symbol, dict.index(new_state))), state.paths)
        new_auto.append(node(dict.index(state.id), new_paths, state.accept))
    return new_auto

##################################################

#if __name__ == "__main__":
#    automata = [node(0, [('1', 1)], False), node(1, [('2', 1), ('1', 2)], False), node(2, [], True)]
#    imitate_automata(automata, "122222121")
#    aut2 = [node(0, [('1', 1), (None, 1)], False), node(1, [('2', 1), ('1', 2), ('1', 1), (None, 2)], False), node(2, [], True)]
#    print get_epsilon_closure([0, 1], aut2)