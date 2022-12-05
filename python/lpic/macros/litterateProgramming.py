
import yaml

import lpic.ninja
import lpic.parser

class CodeHolder :
  def __init__(self, codeType) :
    self.codeType  = codeType
    self.someLines = []
    self.saved     = False

  def addCode(self, someLines) :
    self.someLines.append(someLines)

def dealWithTypedCode(aCodeType, aParser, anIndex) :
  pState = lpic.parser.Parser.state

  stopStr = 'stop'+aCodeType
  someLines = []
  while True :
    aParser.nextLine()
    if stopStr in aParser.curLine :
      if aCodeType not in pState.state :
        pState.state[aCodeType] = CodeHolder(aCodeType)
      pState.state[aCodeType].addCode(someLines)
      break
    someLines.append(aParser.curLine)

  if pState.state[aCodeType] :
    print(pState.state[aCodeType].codeType)
    print(yaml.dump(pState.state[aCodeType].someLines))

def setupTypedCode(aCodeType) :
  def _dealWithTypedCode(aParser, anIndex) :
    dealWithTypedCode(aCodeType, aParser, anIndex)
  lpic.parser.Parser.registerMacro(
    'start'+aCodeType,
    _dealWithTypedCode
  )

setupTypedCode('CCode')
setupTypedCode('CHeader')
setupTypedCode('LuaCode')
setupTypedCode('MkIVCode')
setupTypedCode('MpIVCode')
