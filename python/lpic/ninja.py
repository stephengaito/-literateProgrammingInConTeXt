
import yaml

nVars = {}

nRules = {}

nBuilds = {}

def getVars() :
  return nVars

def addVar(varName, varValue) :
  if varName in nVars :
    print(f"Over writing existing variable: [{varName}]" )
  nVars[varName] = varValue

def getRules() :
  return nRules

def addRule(ruleName, ruleCmd, ruleVars={}) :
  if ruleName in nRules :
    print(f"Over writing existing rule: [{ruleName}]")
  ruleVars['command'] = ruleCmd
  nRules[ruleName] = ruleVars

def getBuilds() :
  return nBuilds

def addBuild(artefact, ruleName) :
  if artefact in nBuilds :
    print(f"Over writing existing build artefact [{artefact}]")
  nBuilds[artefact] = {
    'ruleName'     : ruleName,
    'dependencies' : [],
    'outputs'      : [ artefact ]
  }

def addDependency(artefact, dependency) :
  if artefact not in nBuilds :
    print(f"No existing build rule for [{artefact}]")
    return
  nBuilds[artefact]['dependencies'].append(dependency)

def writeOutNinjaFile(aFileIO) :
  aFileIO.write("\n------------------------------------------------------\n")
  aFileIO.write("ninja vars:\n")
  aFileIO.write(yaml.dump(nVars))
  aFileIO.write("\n------------------------------------------------------\n")
  aFileIO.write("ninja rules:\n")
  aFileIO.write(yaml.dump(nRules))
  aFileIO.write("\n------------------------------------------------------\n")
  aFileIO.write("ninja builds:\n")
  aFileIO.write(yaml.dump(nBuilds))
  aFileIO.write("\n------------------------------------------------------\n")
