
import lpc.dsl

def dealWithComponent(anReMatch) :
  if not anReMatch : return
  subContextPath = anReMatch.group(1)
  lpc.dsl.parse(subContextPath+'.tex')

lpc.dsl.registerMacro(
  'component',
  '\\\\component\s+(\S+)\s*',
  dealWithComponent
)