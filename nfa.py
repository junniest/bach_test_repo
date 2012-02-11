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

def get_epsilon_closure (automata):
  if isinstance (automata, char_nfa):
    return [automata]
  elif isinstance (automata, asterix_nfa):
    a = get_epsilon_closure(automata.content)
    a.append(automata.nxt)
    a.append(automata)
    return a
  elif isinstance (automata, or_nfa):
    a = get_epsilon_closure(automata.alternative[0])
    b = get_epsilon_closure(automata.alternative[1])
    b.append(automata)
    return a + b
  elif isinstance (automata, done_nfa):
    return [automata]
  elif automata is None:
    return None
  return None

#def get_moves (automata, symbol):
#  if isinstance (automata, char_nfa):
#    if automata.character == symbol:
#      return [automata]
#    else:
#      return []
#  elif isinstance (automata, asterix_nfa):
#    if automata.content.charachter == symbol:
#      return [automata.content]
#    else:
#      return []
#  elif isinstance (automata, or_nfa):
#    list = []
#    if automata.alternative[0].charachter == symbol:
#      list.append(automata.alternative[0])
#    if automata.alternative[1].charachter == symbol:
#      list.append(automata.alternative[1])
#    return list
#  elif isinstance (automata, done_nfa):
#    return None
#  elif automata is None:
#    return None
#  return None


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

a = get_epsilon_closure (f.nxt)
for item in a:
    item.xprint_one ()

print
print
enumerate_states (f)

f.xprint ()

def parse (string):
    pass
    
        
        
        
     
