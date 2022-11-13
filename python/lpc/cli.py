import re
import sys
import aiofiles

from lpc.dsl import parse

import lpc.macros.baseContext
import lpc.macros.litterateProgramming

lpc.dsl.showMacros()

def usage() :
  print("""
lpc processes a context file looking for significant control macros to
build a map of how to build the document and its associated software.

usage: lpc [options] <contextFile>

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
  parse(contextPath)
