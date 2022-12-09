
import re
import sys
import yaml

import lpic.ninja
import lpic.parser

def codeError(aMsg) :
  print(aMsg)
  sys.exit(1)

class CodeHolder :
  def __init__(self, fileName, codeType) :
    self.fileName  = fileName
    self.codeType  = codeType
    self.someLines = []
    self.saved     = False

  regExps     = {}
  codeHolders = {}

  def addCode(self, someLines) :
    self.someLines.append(someLines)

def dealWithCreateTypedCode(aCodeType, aParser, anIndex) :
  aMatch = CodeHolder.regExps[aCodeType]['creates'].match(aParser.curLine, anIndex)
  if not aMatch or not aMatch.group(1) :
    codeError(f"Could not find file name in {aParser.curLine}")
  fileName = aMatch.group(1)
  newCodeHolder = CodeHolder(fileName, aCodeType)
  lpic.parser.Parser.state.state[aCodeType] = newCodeHolder
  CodeHolder.codeHolders[aCodeType][fileName] = newCodeHolder

def dealWithTypedCode(aCodeType, aParser, anIndex) :
  pState = lpic.parser.Parser.state

  stopStr = 'stop'+aCodeType
  someLines = []
  while True :
    aParser.nextLine()
    if stopStr in aParser.curLine :
      if aCodeType not in pState.state :
        print(f"  No {aCodeType} holder currently defined!")
        codeError(f"  Did you forget a \\creates{aCodeType} macro?")
      pState.state[aCodeType].addCode(someLines)
      break
    someLines.append(aParser.curLine)

  if pState.state[aCodeType] :
    print(yaml.dump(pState.state[aCodeType]))

def setupTypedCode(aCodeType, aCodeSaver) :
  if aCodeType not in CodeHolder.codeHolders :
    CodeHolder.codeHolders[aCodeType] = {}
  if aCodeType not in CodeHolder.regExps :
    CodeHolder.regExps[aCodeType] = {}
  CodeHolder.regExps[aCodeType]['creates'] = re.compile(r'\\creates'+aCodeType+r'\{(\S+)\}')
  #print(CodeHolder.regExps[aCodeType]['creates'].pattern)
  def _dealWithCreateTypedCode(aParser, anIndex) :
    dealWithCreateTypedCode(aCodeType, aParser, anIndex)
  lpic.parser.Parser.registerMacro(
    'creates'+aCodeType,
    _dealWithCreateTypedCode
  )
  def _dealWithTypedCode(aParser, anIndex) :
    dealWithTypedCode(aCodeType, aParser, anIndex)
  lpic.parser.Parser.registerMacro(
    'start'+aCodeType,
    _dealWithTypedCode
  )
  lpic.parser.Parser.registerFinalAction(aCodeSaver)

def saveCCode() :
  cCodeHolders = CodeHolder.codeHolders['CCode']
  for aKey, aCodeHolder in cCodeHolders.items() :
    print(f"Saving {aCodeHolder.fileName}.c")

setupTypedCode('CCode', saveCCode)

def saveCHeader() :
  cHeaderHolders = CodeHolder.codeHolders['CHeader']
  for aKey, aCodeHolder in cHeaderHolders.items() :
    print(f"Saving {aCodeHolder.fileName}.h")

setupTypedCode('CHeader', saveCHeader)

#setupTypedCode('LuaCode')
#setupTypedCode('MkIVCode')
#setupTypedCode('MpIVCode')
