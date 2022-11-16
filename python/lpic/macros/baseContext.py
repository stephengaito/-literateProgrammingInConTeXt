
import lpic.dsl

def dealWithComponent(anReMatch) :
  if not anReMatch : return
  subContextPath = anReMatch.group(1)
  lpic.dsl.parse(subContextPath+'.tex')

lpic.dsl.registerMacro(
  'component',
  '\\\\component\s+(\S+)\s*',
  dealWithComponent
)