import re
import yaml

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
