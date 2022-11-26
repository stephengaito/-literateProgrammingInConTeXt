
import re
import yaml

import lpic.ninja
import lpic.parser

def addTex(contextPath) :
  if '.' not in contextPath : contextPath = contextPath + '.tex'
  return contextPath

def dealWithComponent(anReMatch) :
  if isinstance(anReMatch, str) :
    subContextPath = anReMatch
  elif isinstance(anReMatch, re.Match) :
    subContextPath = anReMatch.group(1)
  else : return

  subContextPath = addTex(subContextPath)
  lpic.parser.pState.artefact = subContextPath
  lpic.parser.pState.pushState(keepState=False)
  lpic.ninja.addBuild(subContextPath, 'context')
  lpic.parser.parse(subContextPath)
  lpic.parser.pState.popState()

lpic.parser.registerMacro(
  'component',
  '\\\\component\s+(\S+)\s*',
  dealWithComponent
)