r"""
HL7 dictionary.
The dictionary contains all the expressions in a terser format of all the values of a parsed message.
For a segment PID
PID|1||12345^5^M10^Memphis_Hosp^PI||EVERYMAN^ADAM^^JR^^^L|19800101|M

The dictionary contains theses couples (key, value)
    PID-1   : 1
    PID-3-1 : 12345
    PID-3-2 : 5
    PID-3-3 : M10
    PID-3-4 : Memphis_Hosp
    PID-3-5 : PI
    PID-5-1 : EVERYMAN
    PID-5-2 : ADAM
    PID-5-4 : JR
    PID-5-7 : L
    PID-6   : 19800101
    PID-7    : M

Once the message parsed, the dictionary is used in a classical way
>>> hl7p=hl7parser.HL7Parser()
>>> myhl7dict=hl7p.parse(hl7message)
>>> len(myhl7dict.keys())
86

>>> for key, values in myhl7dict.items():
...    print(key, values)

OBR[1]-02-01 12345678
OBR[1]-02-02 gastric
PV1[1]-18 12345
SPM[3]-17 200309060815


>>> "MSH-4" in myhl7dict
False

"""
from functools import reduce
import json
import re

__author__ = 'Frederic Laurent'
__version__ = "1.0"
__all__ = ["HL7Dict"]

try:
    # python 2
    from UserDict import UserDict
except:
    # python 3
    from collections import UserDict


class HL7Dict(UserDict):
    def __init__(self, terser_separator="-"):
        UserDict.__init__(self)
        self.sep = terser_separator
        self.orderedKeys = []
        self.aliasKeys = {}
        self.aliasSegmentName = {}
        self.currentLineNumber = 0
        self.reZeroLeft = re.compile("0+([1-9]+)")

    def __setitem__(self, key, item):
        # get the qualified name of the segment of current line
        # eg. PID[1] or MSH[1]
        segName = self.lineMap[self.currentLineNumber]

        # build the qualified name and store (ex : MSH[1]-09-01)
        qualName = "%s%s%s" % (segName, self.sep, key)
        self.orderedKeys.append(qualName)
        self.data[qualName] = item

        # build alias
        # MSH[1]-09-01 is aliased MSH-9-1
        # SPM[2]-01 is aliased SPM[2]-1

        if segName in self.aliasSegmentName:
            aliasName = "%s%s%s" % (self.aliasSegmentName[segName], self.sep, self.reZeroLeft.sub("\\1", key))
        else:
            aliasName = "%s%s%s" % (segName, self.sep, self.reZeroLeft.sub("\\1", key))

        self.aliasKeys[aliasName] = qualName
        self.aliasKeys[qualName] = aliasName

    def __contains__(self, key):
        return key in self.aliasKeys

    def __getitem__(self, key):
        return self.get(key)

    def getAliasedKeys(self):
        return list(map(lambda x: self.aliasKeys[x], self.data.keys()))

    def get(self, terser):
        """
            Get a value in the HL7 dictionary. The terser can be fully qualified or not.
            Fully qualified : OBR[1]-10-01
            Simpliest form  : OBR-10-1 (in this case, 1 uniq segment OBR is present in the HL7 message)

            :return : the value or a list of values. Otherwise None.
        """
        key = terser
        # if the expression in not found n the qualified names
        # find the alias
        if terser not in self.data and terser in self.aliasKeys:
            key = self.aliasKeys[terser]

        value = self.data.get(key, None)

        # if the value is not found, it can be a partial terser
        if value:
            return value
        else:
            # find the values : simple startswith : should it be a regexp ? (more powerful, more slower)
            values = list(filter(lambda k: k.startswith(key), self.aliasKeys))
            if len(values) > 0:
                return values
            else:
                return None

    def getSegmentKeys(self, segment):
        """
            Get the different keys for 1 defined segment
            :param segment: Segment to find. Ex : PV1, PID
        """
        return list(filter(lambda x: x.startswith(segment), self.getAliasedKeys()))

    def getSegmentsList(self):
        """
            Get the list of the segments in the HL7 message
        """
        return list(self.segmentNameCount.keys())

    def toJSON(self):
        k, v = self.optimalRepr()
        return json.dumps(dict(zip(k, v)))

    def optimalRepr(self):
        keys = list(map(lambda k: self.aliasKeys[k], self.orderedKeys))
        values = list(map(lambda k: self.get(k), keys))
        return keys, values

    def __repr__(self):
        result = []
        k, v = self.optimalRepr()
        for ind in range(len(k)):
            result.append("'%s': '%s'" % (k[ind], v[ind]))

        return "{%s}" % ", ".join(result)

    def toString(self):
        """
            Return a printable view of the dictionary
        """
        result = []
        k, v = self.optimalRepr()
        longest = reduce(lambda x, y: x if x > len(y) else len(y), k, 0)
        for ind in range(len(k)):
            result.append("%s : %s" % (k[ind].ljust(longest), v[ind]))
        return "\n".join(result)

    def setSegmentsMap(self, segmentNameCount, lineMap):
        """
            Set the segments map
            :param segmentNameCount: a dict with the segment name and the total number of segments with this name
            :param lineMap: a list with the concerned segment. If the PV1 segment is the third if the HL7 message,
            the element in the lineMap list at the third index will be PV1. If there are 3 SPM segments (line 9,10,11)
            in the HL7 message, this list contains 3 elements SPM at index 9,10,11.
        """
        self.segmentNameCount = segmentNameCount
        self.lineMap = lineMap

        #Build an alias map for simplicity in get
        # PID is an alias of PID[1] if only 1 PID segment is present
        for segName in segmentNameCount.keys():
            if segmentNameCount[segName] == 1:
                self.aliasSegmentName[segName] = segName+"[1]"
                self.aliasSegmentName[segName+"[1]"] = segName