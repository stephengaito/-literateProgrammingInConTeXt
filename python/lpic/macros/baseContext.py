
import os
import re
import yaml

import lpic.ninja
import lpic.parser

import lpicBuildRules.context

#def addTex(contextPath) :
#  if '.' not in contextPath : contextPath = contextPath + '.tex'
#  return contextPath

componentRE = re.compile('\\\\component\s+(\S+)\s*')

def dealWithComponent(aParser, anIndex) :
  # process this component...
  #
  anReMatch = componentRE.match(
    aParser.curLine,
    anIndex
  )
  pState  = lpic.parser.Parser.state
  componentPath = anReMatch.group(1)
  aParser = lpic.parser.Parser(componentPath)
  if pState.curPdfBuilder :
    curPdfBuilder = pState.curPdfBuilder
    curPdfBuilder.addImplicitDep(aParser.contextPath)
    pState.pushState()
    if pState.prevBuilders is None :
      lpic.ninja.Builds.addDefaultBuild(curPdfBuilder.buildName)
      pState.prevBuilders = []
    pState.prevBuilders.append(curPdfBuilder)

  componentName = componentPath.removesuffix('.tex')
  pdfBuildName = componentName+'.pdf'
  pState.curPdfBuilder = lpic.ninja.Builds(pdfBuildName, pdfBuildName, 'context')
  pState.curPdfBuilder.addExplicitDep(aParser.contextPath)
  aParser.runMacros()

  pState.popState()

lpic.parser.Parser.registerMacro(
  'component',
  dealWithComponent
)
