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
    """
    indexformat : None (default) or "%02d" style for index in 01,02,etc. style
    """
    TERSER_SEP = '-'

    def __init__(self, terser_separator=TERSER_SEP, indexformat=None):
        self.tersersep = terser_separator
        self.indexformat = indexformat
        self.segment_len = 3
        self.separator_count = 5
        self.header_segment = 'MSH'

    def changeDefaultMessageConst(self, header_segment, segment_len, separator_count):
        """
        Provide a way to change default HL7 parameter if you want to subclass
        :param header_segment: Expected segment, for HL7, it's MSH
        :param segment_len: Expected length of segment, for HL7, it's 3
        :param separator_count: Expected count of separators, for HL7, it's 5
        :return: None
        """
        self.header_segment = header_segment
        self.segment_len = segment_len
        self.separator_count = separator_count

    def extractSeparators(self, hl7dict, msg):
        """ Read from the MSH (Message Header) the separators used to separate the pieces
        of data
        Ex: In the message
        MSH|^~\&|OF|Chemistry|ORT||200309060825||ORU^R01^ORU_R01|msgOF105|T|2.5|123||||USA||EN

        The values separator are ^~\&|

        See HL7 Chapter 2

        """
        assert msg[:self.segment_len] == self.header_segment, \
            "Message MUST start with the %s segment : Here %s" % (self.header_segment, msg[:self.segment_len])
        hl7dict.separators = msg[self.segment_len:self.segment_len+self.separator_count]
        # ['|', '^', '~', '\\', '&']

    def extractSubComponents(self, dictValues, terser, field):
        # extract sub components
        subcomponents = field.split(dictValues.separators[4])

        if len(subcomponents) == 1:
            self.emit(dictValues, terser, subcomponents[0])
        else:
            for index in range(len(subcomponents)):
                idx = str(self.indexformat % (index + 1) if self.indexformat is not None else (index + 1))
                self.emit(dictValues, terser + self.tersersep + idx, subcomponents[index])

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
                idx = str(self.indexformat % (index_compo + 1) if self.indexformat is not None else (index_compo + 1))
                self.extractSubComponents(dictValues, terser + self.tersersep + idx, components[index_compo])

    def extractOccurrences(self, dictValues, terser, field):
        # extract occurrences separated by ~ character by default
        occurrences = field.split(dictValues.separators[2])

        for index_occu in range(len(occurrences)):
            parent = terser
            if len(occurrences) > 1:
                idx = str(self.indexformat % (index_occu + 1) if self.indexformat is not None else (index_occu+1))
                parent += f'[{idx}]'
            # get the components inside
            self.extractComponents(dictValues, parent, occurrences[index_occu])

    def extractValues(self, dictValues, line):
        # fields | separated by default
        fields = line.split(dictValues.separators[0])

        if fields[0] == self.header_segment:
            fields.insert(1, dictValues.separators[0])

        for index in range(1, len(fields)):
            idx = str(self.indexformat % index if self.indexformat is not None else index)

            if len(fields) > 1 and fields[0] == self.header_segment and index in (1, 2):
                self.emit(dictValues,  idx, fields[index])
            else:
                self.extractOccurrences(dictValues,  idx, fields[index])

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
        line_map = ['']
        segment_name_count = {}

        # walk the lines
        for line in lines:
            # get the segment name
            name = line[:self.segment_len]
            # inc the segment count
            if name not in segment_name_count:
                segment_name_count[name] = 1
            else:
                segment_name_count[name] += 1

            qualifiedSegmentName = "%s[%d]" % (name, segment_name_count[name])
            line_map.append(qualifiedSegmentName)

        # return the list of qualified segment name
        # ['', 'MSH[1]', 'PID[1]', 'PV1[1]', 'ORC[1]', 'OBR[1]', 'TQ1[1]', 'OBX[1]', 'SPM[1]', ...
        return segment_name_count, line_map

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
        line_number = 1

        # build the map of segments
        segment_name_count, line_map = self.buildSegmentMap(lines)
        dictValues.setSegmentsMap(segment_name_count, line_map)

        # Parse each line of the message : 1 line = 1 segment
        for line in lines:
            dictValues.currentLineNumber = line_number
            self.extractValues(dictValues, line)
            line_number += 1

        return dictValues
