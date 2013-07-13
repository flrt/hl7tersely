import os
from hl7tersely.hl7parser import HL7Parser

__author__ = 'Frederic Laurent'

def main():
    # Load HL7 data from a file
    hl7text=""
    with open(os.sep.join(["..", "test", "samples", "lab1-neworder-19_3_3_1.hl7"]), "r") as hl7f:
            hl7text = hl7f.read()

    # Parse data
    hl7parser = HL7Parser()
    hl7dict = hl7parser.parse(hl7text)

    # access data
    # print HL7 data, hl7dict is a UserDict
    print(hl7dict)

    # get a list : one key, one value per line
    print(hl7dict.toString())

if __name__ == '__main__':
    main()