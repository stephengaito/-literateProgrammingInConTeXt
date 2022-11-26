
import copy
import re
import yaml

#########################################################################
# state


class ParserState :
  def __init__(self) :
    super().__setattr__('state', {})
    super().__setattr__('stack', [])

  def __setattr__(self, name, value) :
    self.state[name] = value

  def __getattr__(self, name) :
    if name in self.state :
      return self.state[name]
    return None

  def stackDepth(self) :
    return len(self.stack)

  def showState(self) :
    print("---------------------------")
    print(yaml.dump(self.state))
    print("---------------------------")
    print(yaml.dump(self.stack))
    print("---------------------------")

  def pushState(self, keepState=False) :
    self.stack.append(self.state)
    if keepState : super().__setattr__('state', self.state.deepcopy())
    else :         super().__setattr__('state', {})

  def popState(self) :
    if 0 < len(self.stack) : super().__setattr__('state', self.stack.pop())
    else                   : super().__setattr__('state', {})

pState = ParserState()

#########################################################################
# macros

macros = {}

def registerMacro(macroProbe, macroRE, macroAction) :
  if not macroProbe.startswith('\\') :
    macroProbe = '\\'+macroProbe
  if macroProbe in macros :
    print(f"You can not register an existing macro {macroProbe}")
    return
  macros[macroProbe] = {
    're'     : re.compile(macroRE),
    'action' : macroAction
  }

def showMacros() :
  print(yaml.dump(macros))

#########################################################################
# parser

def removeComment(aLine) :
  parts = aLine.split('%')
  newLine = []
  while True :
    if len(parts) < 1 : break
    firstPart = parts.pop(0)
    newLine.append(firstPart)
    if not firstPart.endswith('\\') : break
  return "%".join(newLine)

macroRE = re.compile("\\\\\w+")

def parse(contextPath) :
  print(f"opening {contextPath}")
  try :
    if not contextPath.endswith('.tex') : contextPath = contextPath+'.tex'
    with open(contextPath, 'r') as contextFile :
      for aLine in contextFile :
        aLine = aLine.strip()
        aLine = removeComment(aLine)
        probes = macroRE.findall(aLine)
        for aProbe in probes :
          print(aProbe)
          if aProbe in macros :
            index = aLine.find(aProbe)
            print(f"Found {aProbe} at {index} in [{aLine}]")
            anReMatch = macros[aProbe]['re'].match(aLine, index)
            macros[aProbe]['action'](anReMatch)
  except FileNotFoundError :
    pass # we quitely ignore this error since ConTeXt does as well!
