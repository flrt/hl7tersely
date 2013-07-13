import os
from hl7tersely.hl7parser import HL7Parser

__author__ = 'Frederic Laurent'

def main():
    # Load HL7 data from a file
    hl7text=""
    with open(os.sep.join(["..", "test", "samples", "lab3-statuschanged-19_3_3_7.hl7"]), "r") as hl7f:
            hl7text = hl7f.read()

    # Parse data
    hl7parser = HL7Parser()
    hl7dict = hl7parser.parse(hl7text)

    print("Message type : %s" % hl7dict["MSH-9-3"])
    print("Patient ID   : %s" % hl7dict["PID-3-1"])

    print("Is there a SSN Number ? : %s " % ("PID-19" in hl7dict))

    # Get all the tersers for all OBX segments
    obx_tersers = hl7dict.getSegmentKeys("OBX")
    obx3_list = list(filter(lambda t: t.endswith("]-3-2"), obx_tersers))
    for obx3 in obx3_list:
        print(" - %s " % hl7dict[obx3])

if __name__ == '__main__':
    main()