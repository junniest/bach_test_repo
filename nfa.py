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

  def add_next_state (self, state):
    if self.start is None or self.end is None:
      raise Exception ("Abstract nfa instantiated")
    else:
      self.end.nxt = state.start
      self.end = state.end
      self.count += state.count
    
    return self

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
      
    if (self.nxt is not None):
      print "->",
      self.nxt.xprint ()

class node_dfa:
  def __init__ (self, nfa_state_list):
    id = []
    for i in nfa_state_list:
      id.append(i.num)
    self.id = "".join([str(x) for x in sorted(id)])
    self.states = nfa_state_list

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
    self.count = state.count + 1

class or_nfa (nfa):
  def __init__ (self, state0, state1):
    nfa.__init__ (self)
    self.alternative = (state0, state1)
    self.start = self
    self.end = self
    self.count = state0.count + state1.count + 1

class done_nfa (nfa):
  def __init__ (self):
    nfa.__init__ (self)
    self.start = self
    self.end = self
    self.count = 1

def enumerate_states (automata, start=0):
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
  elif automata is None:
    return start
  return enumerate_states (automata.nxt, start)

def add_to_state_list (nfa_state_list, dfa_state_list):
  new_dfa_state = node_dfa(nfa_state_list)
  is_in_list = False
  for dfa_state in dfa_state_list:
    if dfa_state.id == new_dfa_state.id:
      is_in_list = True
      break
  if not is_in_list:
    dfa_state_list.append(new_dfa_state)
  return dfa_state_list

def determinate (automata, dfa_state_list=[]):
  nfa_state_list = get_epsilon_closure(automata)
  if nfa_state_list:
    dfa_state_list = add_to_state_list(nfa_state_list, dfa_state_list)
  if isinstance (automata, char_nfa):
    pass
  elif isinstance (automata, asterix_nfa):
    determinate (automata.content)
  elif isinstance (automata, or_nfa):
    determinate (automata.alternative[0])
    determinate (automata.alternative[1])
  elif isinstance (automata, done_nfa):
    pass
  elif automata is None:
    return
  determinate (automata.nxt, dfa_state_list)
  return dfa_state_list

def get_epsilon_closure (automata):
  if isinstance (automata, char_nfa):
    return [automata]
  elif isinstance (automata, asterix_nfa):
    closure = get_epsilon_closure(automata.content)
    closure.append(automata.nxt)
    closure.append(automata)
    return closure
  elif isinstance (automata, or_nfa):
    closure = get_epsilon_closure(automata.alternative[0])
    closure1 = get_epsilon_closure(automata.alternative[1])
    closure1.append(automata)
    return closure + closure1
  elif isinstance (automata, done_nfa):
    return [automata]
  elif automata is None:
    return None
  return None

# a(a|b)x*
f = char_nfa ('a') \
    .add_next_state (or_nfa (char_nfa ('a'), char_nfa ('b'))) \
    .add_next_state (asterix_nfa (char_nfa ('x'))) \
    .add_next_state (done_nfa ())

# a(a|b)*
f = char_nfa('a').add_next_state(asterix_nfa(or_nfa(char_nfa('a'), char_nfa('b')))).add_next_state(done_nfa())

f.xprint ()
print f.count

print
print
enumerate_states (f)
f.xprint ()

for i in determinate(f):
    if i is not None:
        print '------------------------'
        for j in i.states:
            j.xprint_one ()
            print ';'