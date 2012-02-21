__author__ = "Artem Shinkarov"
__date__ = "2012-02-09"

"NFA class for regular expressions"

class nfa (object):
  def __init__ (self):
    self.start = None
    self.end = None
    self.nxt  = None
    self.num = None
    self.count = 0
    self.last_in_content = False

  def add_next_state (self, state):
    if self.start is None or self.end is None:
      raise Exception ("Abstract nfa instantiated")
    else:
      tmp = self.end
      self.end.nxt = state.start
      self.end = state.end
      self.count += state.count
      tmp.add_to_last_state (tmp, state.start)
    return self

  def add_to_last_state (self, state0, state1):
    if isinstance (self, or_nfa):
      print "add_to_last_state OR NFA"
      self.alternative[0].end.nxt = state1
      self.alternative[1].end.nxt = state1
      self.alternative[0].add_to_last_state (state0, state1)
      self.alternative[1].add_to_last_state (state0, state1)
    elif isinstance (self, asterix_nfa):
      print "add_to_last_state ASTERIX NFA"
      self.content.end.nxt = state0
      self.content.add_to_last_state (state0, state1)

  def xprint_one(self):
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

  def xprint (self):
    self.xprint_one()
      
    if self.nxt is not None and not self.last_in_content:
      print "->",
      self.nxt.xprint ()
    if self.last_in_content and self.nxt is not None:
      print "next is", self.nxt.num

""" DFA node class """
class node_dfa:
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

class char_nfa (nfa):
  def __init__ (self, c):
    nfa.__init__ (self)
    self.character = c
    self.count = 1
    self.start = self
    self.end = self

class asterix_nfa (nfa):
  def __init__ (self, state):
    nfa.__init__ (self)
    self.content = state
    self.start = self
    self.end = self
    state.end.last_in_content = True

class or_nfa (nfa):
  def __init__ (self, state0, state1):
    nfa.__init__ (self)
    self.alternative = (state0, state1)
    self.start = self
    self.end = self
    self.count = state0.count + state1.count + 1
    state0.end.last_in_content = True
    state1.end.last_in_content = True

class done_nfa (nfa):
  def __init__ (self):
    nfa.__init__ (self)
    self.start = self
    self.end = self
    self.count = 1

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

""" Returns moves possible from the given dfa state (nfa state list) by a specific symbol """
def get_moves (dfa_state, symbol):
  moves = []
  for nfa_state in dfa_state.states:
    if isinstance (nfa_state, char_nfa):
      if nfa_state.character == symbol:
        moves.append(nfa_state.nxt)
  return moves

""" Epsilon closure for a list of states """
def get_epsilon_closure (nfa_state_list):
  closure = []
  for state in nfa_state_list:
    closure_one = get_epsilon_closure_single (state)
    if closure_one:
      closure = closure + closure_one
  if closure:
    return closure
  return None

""" Epsilon closure for a single state """
def get_epsilon_closure_single (automata):
  if isinstance (automata, char_nfa):
    return [automata]
  elif isinstance (automata, asterix_nfa):
    closure = get_epsilon_closure_single (automata.content)
    closure.append (automata.nxt)
    closure.append (automata)
    return closure
  elif isinstance (automata, or_nfa):
    closure = get_epsilon_closure_single (automata.alternative[0])
    closure1 = get_epsilon_closure_single (automata.alternative[1])
    closure1.append (automata)
    return closure + closure1
  elif isinstance (automata, done_nfa):
    return [automata]
  elif automata is None:
    return None
  return None

""" Gets first unmarked state from the dfa state list, which means that it wasn't processed yet """
def get_unmarked (dfa_state_list):
  new_list = filter(lambda x: not x.marked, dfa_state_list)
  if new_list:
    return new_list[0]
  return None

""" Returns a dfa state to which the given nfa path leads. """
def get_state_to (nfa_state, dfa_state_list):
  if nfa_state.nxt is None:
    print "No next state"
    return None
  id = str (nfa_state.nxt.num)
  for dfa_state in dfa_state_list:
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
  return dfa_state_list

def determinate (automata, symbol_list):
  dfa_state_list = []
  nfa_state_list = get_epsilon_closure_single (automata)
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



# a(a|b)x*
#f = char_nfa ('a') \
#    .add_next_state (or_nfa (char_nfa ('a'), char_nfa ('b'))) \
#    .add_next_state (asterix_nfa (char_nfa ('x'))) \
#    .add_next_state (done_nfa ())

# (a|b)*
f = asterix_nfa(or_nfa(char_nfa('a'), char_nfa('b'))).add_next_state(done_nfa())

# (ab*|bb)
f = or_nfa(char_nfa('a').add_next_state(asterix_nfa(char_nfa('b'))), char_nfa('b').add_next_state(char_nfa('b'))).add_next_state(done_nfa())

enumerate_states (f)
f.xprint ()
print

for i in determinate(f, 'abx'):
    if i is not None:
        print '------------------------'
#        print i.id
#        for j in i.states:
#            j.xprint ()
#            print ';'
        i.xprint ()