
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

  def pushState(self, keepState=True) :
    self.stack.append(self.state)
    if keepState : super().__setattr__('state', copy.deepcopy(self.state))
    else :         super().__setattr__('state', {})

  def popState(self) :
    if 0 < len(self.stack) : super().__setattr__('state', self.stack.pop())
    else                   : super().__setattr__('state', {})

class Parser :

  state = ParserState()

  finalActions = []

  @classmethod
  def registerFinalAction(cls, aFinalAction) :
    cls.finalActions.append(aFinalAction)

  @classmethod
  def runFinalActions(cls, config) :
    for anAction in cls.finalActions :
      anAction(config)

  #########################################################################
  # macros specific class variables and methods

  macros = {}

  @classmethod
  def registerMacro(cls, macroProbe, macroAction) :
    if not macroProbe.startswith('\\') :
      macroProbe = '\\'+macroProbe
    if macroProbe in cls.macros :
      print(f"You can not register an existing macro {macroProbe}")
      return
    cls.macros[macroProbe] = macroAction

  @classmethod
  def showMacros(cls) :
    print(yaml.dump(cls.macros))

  #########################################################################
  # parser specific class variables and methods

  macroRE = re.compile("\\\\\w+")

  #########################################################################
  # parser specific instance variables and methods

  def __init__(self, contextPath) :
    if contextPath.startswith('\\component') :
      # create a fake Parser to hand to
      # lpic.macros.baseContext.dealWithComponent to get everything
      # started
      print(f"New fake parser on [{contextPath}]")
      self.curLine = contextPath
    else :
      if '.' not in contextPath : contextPath = contextPath + '.tex'
      print(f"New parser on [{contextPath}]")
      self.curLine     = None

    self.contextPath = contextPath
    self.contextFile = None
    self.linesIter   = None
    self.probesIter  = None

  def __del__(self) :
    if self.contextFile is not None and not isinstance(self.contextFile, list) :
      self.contextFile.close()

  def removeComment(aLine) :
    aLine = aLine.strip()
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
      try :
        self.contextFile = open(self.contextPath, 'r')
      except FileNotFoundError :
        print(f"Could not open [{self.contextPath}]")
        self.contextFile = []
    for aLine in self.contextFile :
      self.curLine = aLine.rstrip()
      yield self.curLine
    self.curLine = None
    yield self.curLine

  def nextLine(self) :
    if self.linesIter is None :
      self.linesIter = self.__lineIter__()
    return next(self.linesIter, None)

  def __probeIter__(self) :
    if self.curLine is None : self.nextLine()
    while self.curLine  is not None :
      curLine = Parser.removeComment(self.curLine)
      curProbes = type(self).macroRE.findall(curLine)
      for aProbe in curProbes :
        yield aProbe
      self.nextLine()
    yield None

  def nextProbe(self) :
    if self.probesIter is None :
      self.probesIter = self.__probeIter__()
    return next(self.probesIter, None)

  def runMacros(self) :
    aProbe = self.nextProbe()
    while aProbe :
      print(aProbe)
      if aProbe in type(self).macros :
        index = self.curLine.find(aProbe)
        print(f"Found {aProbe} at {index} in [{self.curLine}]")
        type(self).macros[aProbe](self, index)
      aProbe = self.nextProbe()
