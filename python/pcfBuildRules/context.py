
import os
import yaml

from lpic.ninja import Vars, Rules, Builds

def addContextVars() :
  if not Vars.hasVar('contextDir') :
    baseDir = __file__.split(os.path.sep)
    baseDir.pop()
    baseDir.pop()
    baseDir = os.path.join(os.path.sep, *baseDir)
    cwdir = os.getcwd()
    contextDir = '.'+cwdir.removeprefix(baseDir)
    Vars.addVar('contextDir', contextDir)

addContextVars()


def addContextRules() :
  if not Rules.hasRule('context') :
    Rules('context', 'newTask --dir $contextDir -- $out context $in')

addContextRules()
