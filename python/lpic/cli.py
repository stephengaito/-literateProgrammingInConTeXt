import os
import re
import sys
import yaml

# Find the build rules (and base of pyComputeFarm directories)

def findBuildRules() :
  workingDir = os.getcwd().split(os.path.sep)
  while 1 < len(workingDir) :
    workingDir.pop()
    lpicBuildRules = os.path.join(os.path.sep, *workingDir, 'lpicBuildRules')
    if os.path.exists(lpicBuildRules) :
      sys.path.append(os.path.join(os.path.sep, *workingDir))
      return
  print("Could not find the lpic build rules directory")
  print("in any of the parent directories above:\n")
  print(f"  {os.getcwd()}")
  print("\nPlease provide your build rules and try again!")
  sys.exit(1)

findBuildRules()

# The next two modules are used by the macros...
import lpic.ninja
import lpic.parser

import lpic.macros.baseContext
#import lpic.macros.litterateProgramming

def usage() :
  print("""
lpic processes a context file looking for significant control macros to
build a map of how to build the document and its associated software.

usage: lpic [options] <contextFile>

contextFile the path to the conTeXt file to be processed.

options:

 -h, --help Print this list of options

  """)
  sys.exit(1)

def cli() :
  sys.argv.pop(0)
  for anArg in sys.argv :
    if "-h" in anArg or "--help" in anArg : usage()
  if len(sys.argv) < 1 :
    print("No contextFile provided!")
    usage()


  contextPath = sys.argv.pop(0)

  baseParser = lpic.parser.Parser('\\component '+contextPath)

  lpic.macros.baseContext.dealWithComponent(baseParser, 0)

  with open('build.ninja', 'w') as ninjaFile :
    lpic.ninja.writeOutNinjaFile(ninjaFile)
