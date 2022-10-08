import testsuite
from hl7tersely.hl7parser import HL7Parser

lab1NewOrder = testsuite.loadFile("multiple-ipp.hl7")
hl7p = HL7Parser(terser_separator='.')
hl7d = hl7p.parse(lab1NewOrder)

keys, values = hl7d.optimalRepr()
longest = max(keys, key=len)


for idx in range(len(keys)):
    print(f"{keys[idx]:{len(longest)}} : {values[idx]}")