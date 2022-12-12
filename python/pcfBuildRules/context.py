
import os
import yaml

from lpic.ninja import Vars, Rules, Builds

contextDir = '.'

def determineConTeXtDir() :
  global contextDir
  if not Vars.hasVar('contextDir') :
    baseDir = __file__.split(os.path.sep)
    baseDir.pop()
    baseDir.pop()
    baseDir = os.path.join(os.path.sep, *baseDir)
    cwdir = os.getcwd()
    contextDir = '.'+cwdir.removeprefix(baseDir)

determineConTeXtDir()

def addContextVars(config) :
    Vars.addVar('contextDir', contextDir)

def addContextRules(config) :
  if not Rules.hasRule('context') :
    Rules(
      'context',
      'newTask --dir $contextDir -- $out context $in'
    )

def addBuildRules(config) :
  addContextVars(config)
  addContextRules(config)
