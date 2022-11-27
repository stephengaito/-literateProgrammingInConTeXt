
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

class Parser :

  #########################################################################
  # macros specific class variables and methods

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
  # parser specific class variables and methods

  macroRE = re.compile("\\\\\w+")

  #########################################################################
  # parser specific instance variables and methods

  def __init__(contextPath) :
    if '.' not in contextPath : contextPath = contextPath + '.text'
    self.contextPath = contextPath
    self.contextFile = None
    self.linesIter   = None
    self.probesIter  = None
    self.curLine     = None

  def __del__(self) :
    if self.contextFile is not None : self.contextFile.close()

  def removeComment(aLine) :
    parts = aLine.split('%')
    newLine = []
    while True :
      if len(parts) < 1 : break
      firstPart = parts.pop(0)
      newLine.append(firstPart)
      if not firstPart.endswith('\\') : break
    return "%".join(newLine)

  def __lineIter__(self) :
    if self.contextFile is None :
      self.contextFile = open(self.contextPath, 'r')
    for aLine in self.contextFile :
      self.curLine = Parser.removeComment(next(self.linesIter))
      yield self.curLine
    self.curLine = None
    yield self.curLine

  def nextLine(self) :
    if self.linesIter is None :
      self.linesIter = self.__lineIter__()
    return next(self.linesIter, None)

  def nextProbe(self) :
    if self.probesIter is None :
      if self.curLine is None : self.nextLine()
      if self.curLine is None :
        self.curProbe = None
        return self.curProbe
      self.probesIter = macroRE.finditer(self.curLine)
    self.curProbe = next(self.probesIter, None)
    return self.curProbe

  def runNextMacro(self) :
    aProbe = self.nextProbe()
    while aProbe :
      if aProbe in macros :
        index = self.curLine.find(aProbe)
        macros[aProbe]['action'](self, index)
      aProbe = self.nextProbe()

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
