
import os
import sys
import yaml

from lpic.ninja import Vars, Rules, Builds

import lpicBuildRules.context

def getCCodeFlags(config) :
  cflags = []
  if 'externalRequirements' in config :
    for aPkg, requirements in config['externalRequirements'].items() :
      if 'cflags' in requirements :
        pkgCflags = requirements['cflags']
        if isinstance(pkgCflags, str) :
          if pkgCflags not in cflags :
            cflags.append(pkgCflags)
        elif isinstance(pkgCflags, dict) :
          if 'cmd' in pkgCflags :
            result = os.popen(pkgCflags['cmd'])
            if result :
              resultStr = result.read().strip()
              if resultStr not in cflags :
                cflags.append(resultStr)
              result.close()
  return " ".join(cflags)

def getCCodeLibs(config) :
  libs = []
  if 'externalRequirements' in config :
    for aPkg, requirements in config['externalRequirements'].items() :
      if 'libs' in requirements :
        pkgLibs = requirements['libs']
        if isinstance(pkgLibs, str) :
          if pkgLibs not in libs :
            libs.append(pkgLibs)
        elif isinstance(pkgLibs, dict) :
          if 'cmd' in pkgLibs :
            result = os.popen(pkgLibs['cmd'])
            if result :
              resultStr = result.read().strip()
              if resultStr not in libs :
                libs.append(resultStr)
              result.close()
  return " ".join(libs)


def addCCodeVars(config) :
  cflags = getCCodeFlags(config)
  if cflags :
    Vars.addVar('cflags', cflags)
  libs = getCCodeLibs(config)
  if libs :
    Vars.addVar('libs', libs)

def addCCodeRules(config) :
  if not Rules.hasRule('gccX86') :
    Rules(
      'gccX86',
      'newTask --dir $contextDir -- $out gccX86 $cflags -o $out $in'
    )
  if not Rules.hasRule('gccARM') :
    Rules(
      'gccARM',
      'newTask --dir $contextDir -- $out gccARM $cflags -o $out $in'
    )
  if not Rules.hasRule('arX86') :
    Rules(
      'arX86',
      'newTask --dir $contextDir -- $out arX86 $cflags -o $out $in'
    )
  if not Rules.hasRule('arARM') :
    Rules(
      'arARM',
      'newTask --dir $contextDir -- $out arARM $cflags -o $out $in'
    )
  if not Rules.hasRule('ldX86') :
    Rules(
      'ldX86',
      'newTask --dir $contextDir -- $out ldX86 $cflags -o $out $in'
    )
  if not Rules.hasRule('ldARM') :
    Rules(
      'ldARM',
      'newTask --dir $contextDir -- $out ldARM $cflags -o $out $in'
    )


def addBuildRules(config) :
  addCCodeVars(config)
  addCCodeRules(config)
