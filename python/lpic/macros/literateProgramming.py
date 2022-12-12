
import datetime
import os
import re
import sys
import yaml

import lpic.ninja
import lpic.parser

import lpicBuildRules.cCode

def codeError(aMsg) :
  print(aMsg)
  sys.exit(1)

class ApplicationHolder :
  def __init__(self, applicationPath, applicationName) :
    self.applicationPath = applicationPath
    self.applicationName = applicationName
    self.cCodeFiles  = []
    self.cHeaderFiles = []
    self.libraryFiles = []

  applicationHolders = { 'cApp' : {} }

  def addCHeaderFile(self, aCodeHolder) :
    if aCodeHolder not in self.cHeaderFiles :
      self.cHeaderFiles.append(aCodeHolder)

  def addCCodeFile(self, aCodeHolder) :
    if aCodeHolder not in self.cCodeFiles :
      self.cCodeFiles.append(aCodeHolder)

  def addLibraryFile(self, aLibraryHolder) :
    if aLibraryHolder not in self.libraryFiles :
      self.libraryFiles.append(aLibraryHolder)

class LibraryHolder :
  def __init__(self, libraryPath, libraryName) :
    self.libraryPath = libraryPath
    self.libraryName = libraryName
    self.cCodeFiles  = []
    self.cHeaderFiles = []

  libraryHolders = { 'cLib' : {} }

  def addCHeaderFile(self, aCodeHolder) :
    if aCodeHolder not in self.cHeaderFiles :
      self.cHeaderFiles.append(aCodeHolder)

  def addCCodeFile(self, aCodeHolder) :
    if aCodeHolder not in self.cCodeFiles :
      self.cCodeFiles.append(aCodeHolder)

class CodeHolder :
  def __init__(self, filePath, fileName, codeType) :
    self.filePath  = ''
    if filePath is not None :
      self.filePath  = filePath
    self.fileName  = fileName
    self.codeType  = codeType
    self.someLines = []

    if codeType == 'CCode' :
      self.fileExtension = '.c'
      self.singleLineComment = '//'
    elif codeType == 'CHeader' :
      self.fileExtension = '.h'
      self.singleLineComment = '//'
    else :
      self.fileExtension = ''
      self.singleLineComment = ''

  copyrightOwner  = ""
  defaultLicenses = {}
  regExps         = {
    'all'   : {},
    'CCode' : {}
  }
  codeHolders     = {}

  def addLicense(self, config, aFileIO) :
    license = []
    copyrightYear = datetime.date.today().strftime("%Y")
    copyrightOwner = ""
    if 'copyrightOwner' in config :
      copyrightOwner = config['copyrightOwner']
    if 'license' in config :
      if 'MIT' in config['license'].upper() :
        license = [
          f' Copyright {copyrightYear} {copyrightOwner}',
          '',
          ' MIT License',
          '',
          ' Permission is hereby granted, free of charge, to any person',
          ' obtaining a copy of this software and associated documentation',
          ' files (the "Software"), to deal in the Software without',
          ' restriction, including without limitation the rights to use,',
          ' copy, modify, merge, publish, distribute, sublicense, and/or sell',
          ' copies of the Software, and to permit persons to whom the',
          ' Software is furnished to do so, subject to the following',
          ' conditions:',
          '',
          '    The above copyright notice and this permission notice shall',
          '    be included in all copies or substantial portions of the',
          '    Software.',
          '',
          ' THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,',
          ' EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES',
          ' OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND',
          ' NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT',
          ' HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,',
          ' WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING',
          ' FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR',
          ' OTHER DEALINGS IN THE SOFTWARE.'
        ]
      elif 'APACHE' in config['license'].upper() :
        license = [
          f' Copyright {copyrightYear} {copyrightOwner}',
          '',
          ' Licensed under the Apache License, Version 2.0 (the "License");',
          ' you may not use this file except in compliance with the License.',
          ' You may obtain a copy of the License at',
          '',
          '    http://www.apache.org/licenses/LICENSE-2.0',
          '',
          ' Unless required by applicable law or agreed to in writing,',
          ' software distributed under the License is distributed on an "AS',
          ' IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either',
          ' express or implied. See the License for the specific language',
          ' governing permissions and limitations under the License. end'
        ]
    aFileIO.write(self.singleLineComment+" ")
    aFileIO.write(("\n"+self.singleLineComment+" ").join(license))
    aFileIO.write("\n\n")

  def addCHeaderPreAmble(self, aFileIO) :
    aFileIO.write(f"#ifndef {self.fileName.upper()}_H\n")
    aFileIO.write(f"#define {self.fileName.upper()}_H\n\n")

  def addCHeaderPostAmble(self, aFileIO) :
    aFileIO.write("\n#endif\n")

  def getFullPath(self, buildDir) :
    return os.path.join(buildDir, self.filePath, self.fileName+self.fileExtension)

  def addCode(self, someLines) :
    self.someLines.extend(someLines)

  @classmethod
  def addCopyrightOwner(klass, copyrightOwner) :
    klass.copyrightOwner = copyrightOwner

  @classmethod
  def addDefaultLicense(klass, aCodeType, licenseName) :
    klass.defaultLicenses[aCodeType] = licenseName

def matchRegExp(aCodeType, regExpType, aParser, anIndex, partName, defaultArg) :
  aMatch = CodeHolder.regExps[aCodeType][regExpType].match(aParser.curLine, anIndex)
  if not aMatch or len(aMatch.groups()) < 1 :
    codeError(f"Could not find {partName} in {aParser.curLine}")
  firstArg = aMatch.group(1)
  secondArg = None
  if '][' in firstArg :
    argParts = firstArg.split('][')
    firstArg = argParts[0]
    secondArg = argParts[1]
  elif defaultArg < 2 :
    secondArg = firstArg
    firstArg  = None
  return (firstArg, secondArg)

def dealWithCopyrightOwner(aParser, anIndex) :
  (copyrightOwner, _ ) = matchRegExp('all', 'copyrightOwner', aParser, anIndex, 'copyright owner', 2)
  CodeHolder.addCopyrightOwner(copyrightOwner)

CodeHolder.regExps['all']['copyrightOwner'] = re.compile(r'\\copyrightOwner\[([^\]]+)\]')
lpic.parser.Parser.registerMacro(
  'copyrightOwner',
  dealWithCopyrightOwner
)

def dealWithDefaultLicense(aCodeType, aParser, anIndex) :
  (licenseName, _) = matchRegExp(aCodeType, 'defaultLicense', aParser, anIndex, 'license', 2)
  CodeHolder.addDefaultLicense(aCodeType, licenseName)

def dealWithBuildsCodeLibrary(aParser, anIndex) :
  (libPath, libName) = matchRegExp('CCode', 'buildsLibrary', aParser, anIndex, 'library', 1)
  newLibraryHolder = LibraryHolder(libPath, libName)
  lpic.parser.Parser.state.state['cLib'] = newLibraryHolder
  LibraryHolder.libraryHolders['cLib'][libName] = newLibraryHolder

CodeHolder.regExps['CCode']['buildsLibrary'] = re.compile(r'\\buildsCCodeLibrary\[(\S+)\]')
lpic.parser.Parser.registerMacro(
  'buildsCCodeLibrary',
  dealWithBuildsCodeLibrary
)

def dealWithBuildsCodeApplication(aParser, anIndex) :
  (appPath, appName) = matchRegExp('CCode', 'buildsApplication', aParser, anIndex, 'library', 1)
  newApplicationHolder = ApplicationHolder(appPath, appName)
  lpic.parser.Parser.state.state['cApp'] = newApplicationHolder
  ApplicationHolder.applicationHolders['cApp'][appName] = newApplicationHolder

CodeHolder.regExps['CCode']['buildsApplication'] = re.compile(r'\\buildsCCodeApplication\[(\S+)\]')
lpic.parser.Parser.registerMacro(
  'buildsCCodeApplication',
  dealWithBuildsCodeApplication
)

def dealWithCreateTypedCode(aCodeType, aParser, anIndex) :
  (filePath, fileName) = matchRegExp(aCodeType, 'creates', aParser, anIndex, 'file name', 1)
  newCodeHolder = CodeHolder(filePath, fileName, aCodeType)
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
  CodeHolder.regExps[aCodeType]['defaultLicense'] = re.compile(r'\\default'+aCodeType+r'License\[(\S+)\]')
  def _dealWithDefaultLicense(aParser, anIndex) :
    dealWithDefaultLicense(aCodeType, aParser, anIndex)
  lpic.parser.Parser.registerMacro(
    'default'+aCodeType+'License',
    _dealWithDefaultLicense
  )
  CodeHolder.regExps[aCodeType]['creates'] = re.compile(r'\\creates'+aCodeType+r'\[(\S+)\]')
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

def saveCCode(config) :
  buildDir = ""
  if 'buildDir' in config :
    buildDir = config['buildDir']
  cCodeHolders = CodeHolder.codeHolders['CCode']
  for aKey, aCodeHolder in cCodeHolders.items() :
    filePath = aCodeHolder.getFullPath(buildDir)
    print(f"Saving {filePath}")
    os.makedirs(os.path.dirname(filePath), mode=0o755, exist_ok=True)
    with open(filePath, 'w') as fileIO :
      aCodeHolder.addLicense(config, fileIO)
      fileIO.write("\n".join(aCodeHolder.someLines)+"\n")

setupTypedCode('CCode', saveCCode)

def saveCHeader(config) :
  buildDir = ""
  if 'buildDir' in config :
    buildDir = config['buildDir']
  cHeaderHolders = CodeHolder.codeHolders['CHeader']
  for aKey, aCodeHolder in cHeaderHolders.items() :
    filePath = aCodeHolder.getFullPath(buildDir)
    print(f"Saving {filePath}")
    os.makedirs(os.path.dirname(filePath), mode=0o755, exist_ok=True)
    with open(filePath, 'w') as fileIO :
      aCodeHolder.addLicense(config, fileIO)
      aCodeHolder.addCHeaderPreAmble(fileIO)
      fileIO.write("\n".join(aCodeHolder.someLines)+"\n")
      aCodeHolder.addCHeaderPostAmble(fileIO)

setupTypedCode('CHeader', saveCHeader)

#setupTypedCode('LuaCode')
#setupTypedCode('MkIVCode')
#setupTypedCode('MpIVCode')
