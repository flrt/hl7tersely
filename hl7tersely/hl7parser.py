r"""HL7 Parser. Lightweight and simple parsing of HL7 Messages.

Usage:
    >> hl7parser = HL7Parser()
    >> hl7dict = hl7parser.parse(hl7text)
Use hl7dict as a python dictionary


"""

__author__ = 'Frederic Laurent'
__version__ = "1.0"
__copyright__ = 'Copyright 2013, Frederic Laurent'
__all__ = ["HL7Parser"]

from hl7tersely.hl7dict import HL7Dict


class HL7Parser:
    TERSER_SEP = '-'

    def __init__(self, terser_separator=TERSER_SEP):
        self.tersersep = terser_separator
        self.indexformat = "%02d"

    def extractSeparators(self, hl7dict, msg):
        """ Read from the MSH (Message Header) the separators used to separate the pieces
        of data
        Ex: In the message
        MSH|^~\&|OF|Chemistry|ORT||200309060825||ORU^R01^ORU_R01|msgOF105|T|2.5|123||||USA||EN

        The values separator are ^~\&|

        See HL7 Chapter 2

        """
        assert msg[:3] == "MSH", "Message MUST start with the MSH segment : Here %s" % msg[:3]
        hl7dict.separators = msg[3:8]
        # ['|', '^', '~', '\\', '&']


    def extractSubComponents(self, dictValues, terser, field):
        # extract sub components
        subcomponents = field.split(dictValues.separators[4])

        if len(subcomponents) == 1:
            self.emit(dictValues, terser, subcomponents[0])
        else:
            for index in range(len(subcomponents)):
                self.emit(dictValues, terser + self.tersersep + self.indexformat % (index + 1), subcomponents[index])

    def extractComponents(self, dictValues, terser, field):
        # extract components
        components = field.split(dictValues.separators[1])

        if len(components) == 1:
            # only 1 component : don't generate index
            # NK1[2]-6[1] instead of NK1[2]-6[1]-1
            # PID-1 instead of PID-1-1
            self.extractSubComponents(dictValues, terser, components[0])
        else:
            for index_compo in range(len(components)):
                # extract sub components
                self.extractSubComponents(dictValues, terser + self.tersersep + self.indexformat % (index_compo + 1),
                                          components[index_compo])

    def extractOccurrences(self, dictValues, terser, field):
        # extract occurrences separated by ~ character by default
        occurrences = field.split(dictValues.separators[2])

        for index_occu in range(len(occurrences)):
            parent = terser
            if len(occurrences) > 1:
                parent += '[' + "%02d" % (index_occu + 1) + ']'
            # get the components inside
            self.extractComponents(dictValues, parent, occurrences[index_occu])

    def extractValues(self, dictValues, line):
        # fields | separated by default
        fields = line.split(dictValues.separators[0])

        if fields[0] == "MSH":
            fields.insert(1, dictValues.separators[0])

        for index in range(1, len(fields)):
            if len(fields) > 1 and fields[0] == "MSH" and index in (1, 2):
                self.emit(dictValues,  self.indexformat % index, fields[index])
            else:
                self.extractOccurrences(dictValues,  self.indexformat % index, fields[index])

    def emit(self, dictValues, key, value):
        """A new value has been found. This couple : key,value is emitted, and store in the HL7 dictionary.
        """
        if key and value:
            dictValues[key] = value

    def buildSegmentMap(self, lines):
        """ Build the map of the various segments.
        Each segment has a qualified name according to the number
        of equivalent segment.
        If there is only one segment, the segment name is MSH[1] or PID[1].
        If there are 3 segments with the same name, the qualified names are
        SPM[1], SPM[2], SPM[3] for instance.
        SPM[2] is the second SPM segment.

        """
        lineMap = ['']
        segmentNameCount = {}

        # walk the lines
        for line in lines:
            # get the segment name
            name = line[:3]
            # inc the segment count
            if name not in segmentNameCount:
                segmentNameCount[name] = 1
            else:
                segmentNameCount[name] += 1

            qualifiedSegmentName = "%s[%d]" % (name, segmentNameCount[name])
            lineMap.append(qualifiedSegmentName)

        # return the list of qualified segment name
        # ['', 'MSH[1]', 'PID[1]', 'PV1[1]', 'ORC[1]', 'OBR[1]', 'TQ1[1]', 'OBX[1]', 'SPM[1]', ...
        return segmentNameCount, lineMap

    def parse(self, msg):
        """ Parse an HL7 message and return an HL7 dictionary.

        :param msg: HL7 message to parse
        :return: An HL7 dictionary
        """
        #init
        dictValues = HL7Dict(self.tersersep)
        msg_ = msg.strip('\r\n ')

        # extracts separator defined in the message itself
        self.extractSeparators(dictValues, msg_)
        msg_ = msg_.replace('\r', '\n')
        lines = msg_.split('\n')
        lineNumber = 1

        # build the map of segments
        segmentNameCount, lineMap = self.buildSegmentMap(lines)
        dictValues.setSegmentsMap(segmentNameCount, lineMap)

        # Parse each line of the message : 1 line = 1 segment
        for line in lines:
            dictValues.currentLineNumber = lineNumber
            self.extractValues(dictValues, line)
            lineNumber += 1

        return dictValues
