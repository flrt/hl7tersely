import unittest
import os
import sys

from hl7tersely.hl7parser import HL7Parser


def loadFile(filename):
    ab = os.path.abspath(sys.argv[0])
    with open(os.path.dirname(ab) + os.sep + "samples" + os.sep + filename, "r") as hl7f:
        data = hl7f.read()
    return data


class TerserTest(unittest.TestCase):
    lab1NewOrder = loadFile("lab1-neworder-19_3_3_1.hl7")
    lab3StatusChanged = loadFile("lab3-statuschanged-19_3_3_7.hl7")
    multi = loadFile("multiple-ipp.hl7")
    a05 = loadFile("pam31-preadmit-iti-3_5_2.hl7")

    # Can't use with python 2.6
    #     @classmethod
    #     def setUpClass(cls):
    #         cls.lab1NewOrder = loadFile("lab1-neworder-19_3_3_1.hl7")
    #         cls.lab3StatusChanged = loadFile("lab3-statuschanged-19_3_3_7.hl7")
    #         cls.multi = loadFile("multiple-ipp.hl7")
    #         cls.a05 = loadFile("pam31-preadmit-iti-3_5_2.hl7")

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_segcount_lab1(self):
        hl7p = HL7Parser()
        hl7d = hl7p.parse(self.lab1NewOrder)

        pv1_ = hl7d.getSegmentKeys("PV1")
        self.assertEqual(len(pv1_), 4, "Error - the HL7 test file Lab1 New Order contains 4 PV1 fields")

        segs_ = hl7d.getSegmentsList()
        self.assertEqual(len(segs_), 8, "Error - the HL7 test file Lab1 New Order contains 8 segments")
   
        if sys.version_info > (2,7):
            self.assertIn("MSH", segs_, "Error - the MSH segment is missing")
            self.assertIn("PID", segs_, "Error - the PID segment is missing")
            self.assertIn("PV1", segs_, "Error - the PV1 segment is missing")
            self.assertIn("ORC", segs_, "Error - the ORC segment is missing")
            self.assertIn("TQ1", segs_, "Error - the TQ1 segment is missing")
            self.assertIn("OBR", segs_, "Error - the TQ1 segment is missing")
            self.assertIn("OBX", segs_, "Error - the TQ1 segment is missing")
            self.assertIn("SPM", segs_, "Error - the SPM segment is missing")

            self.assertGreater(len(hl7d.keys()), 0, "ERR")
        else:
            self.assertTrue("MSH" in segs_, "Error - the MSH segment is missing")
            self.assertTrue("PID" in segs_, "Error - the PID segment is missing")
            self.assertTrue("PV1" in segs_, "Error - the PV1 segment is missing")
            self.assertTrue("ORC" in segs_, "Error - the ORC segment is missing")
            self.assertTrue("TQ1" in segs_, "Error - the TQ1 segment is missing")
            self.assertTrue("OBR" in segs_, "Error - the TQ1 segment is missing")
            self.assertTrue("OBX" in segs_, "Error - the TQ1 segment is missing")
            self.assertTrue("SPM" in segs_, "Error - the SPM segment is missing")

            self.assertTrue(len(hl7d.keys()) > 0, "ERR")


    def test_segcount_lab3(self):
        hl7p = HL7Parser()
        hl7d = hl7p.parse(self.lab3StatusChanged)
        self.assertEqual(len(hl7d.keys()), 124, 'Error - Terser expression count incorrect')

    def test_getvalues_lab3(self):
        hl7p = HL7Parser()
        hl7d = hl7p.parse(self.lab3StatusChanged)
        #print(hl7d.toString())

        self.assertEqual(hl7d.get("ORC-10-2"), "NURSE", "Error - Terser not found")
        self.assertEqual(hl7d.get("ORC[1]-10-02"), "NURSE", "Error - Terser not found")
        self.assertEqual(hl7d.get("SPM[1]-02-03"), None, "Error - Terser does not exists")

    def test_tersersep_lab3(self):
        hl7p = HL7Parser(terser_separator='_')
        hl7d = hl7p.parse(self.lab3StatusChanged)
        self.assertEqual(hl7d.get('OBR_16_2'), 'PHYSICIAN', 'Error - Terser separator replacement issue')

    def test_commondict_lab3(self):
        hl7p = HL7Parser()
        hl7d = hl7p.parse(self.lab3StatusChanged)

        qualified_keys = list(hl7d.keys())
        aliased_keys = list(hl7d.aliasKeys.keys())
        for qk in qualified_keys:
            self.assertTrue(qk in aliased_keys)

        if sys.version_info > (2, 7):
            self.assertIn("MSH-9-3", hl7d, "Error : MSH-9-3 must be in LAB3 message")
            self.assertIn("MSH[1]-09-03", hl7d, "Error : MSH[1]-09-03 must be in LAB3 message")
            self.assertNotIn("MSH-18", hl7d, "Error : MSH-18 must not be in LAB3 message")
        else:
            self.assertTrue("MSH-9-3" in hl7d, "Error : MSH-9-3 must be in LAB3 message")
            self.assertTrue("MSH[1]-09-03" in hl7d, "Error : MSH[1]-09-03 must be in LAB3 message")
            self.assertFalse("MSH-18" in hl7d, "Error : MSH-18 must not be in LAB3 message")

        self.assertEqual("MSH-18" not in hl7d, True, "Error : MSH-18 must not be in LAB3 message")

        self.assertEqual(hl7d["MSH-9-3"], hl7d.get("MSH-9-3"), "Error : both get method must return same result")
        self.assertEqual(hl7d["MSH-9-3"], "ORU_R01", "Error : both get method must return same result")
        self.assertEqual(hl7d["MSH-9-3"], hl7d.get("MSH[1]-09-03"), "Error : both get method must return same result")
        self.assertEqual(hl7d["MSH[1]-09-03"], hl7d.get("MSH-9-3"), "Error : both get method must return same result")

        if sys.version_info > (2, 7):
            self.assertIsNone(hl7d["MSH-18"], "Error : MSH-18 must not be in LAB3 message. Get must return None")
            self.assertIsNone(hl7d.get("MSH-18"), "Error : MSH-18 must not be in LAB3 message. Get must return None")
        else:
            self.assertEqual(hl7d["MSH-18"], None, "Error : MSH-18 must not be in LAB3 message. Get must return None")
            self.assertEqual(hl7d.get("MSH-18"), None,
                             "Error : MSH-18 must not be in LAB3 message. Get must return None")

        self.assertEqual(hl7d.get("MSH-9-3"), "ORU_R01", "Error : both get method must return same result")

        self.assertEqual(len(hl7d.values()), 124, "Error : LAB3 samples contain 124 values")

    def test_multi(self):
        hl7p = HL7Parser()
        hl7d = hl7p.parse(self.multi)

        self.assertEqual(hl7d["PID-3[1]-1"], "123456789", "Error First IPP is 123456789 in PID-3[1]-1")
        self.assertEqual(hl7d["PID-3[1]-4"], "CHU", "Error First Assigning Authority is CHU in PID-3[1]-4")

        self.assertEqual(hl7d["PID-3[2]-1"], "0411886319605719371016", "Error Second IPP is 123456789 in PID-3[1]-1")
        self.assertEqual(hl7d["PID-3[2]-4-2"], "1.2.250.1.213.1.4.2",
                         "Error Second Assigning Authority OID is PID-3[1]-4-2 = 1.2.250.1.213.1.4.2")

        self.assertEqual(type(hl7d["PID-3[2]-4"]), type([]),
                         "PID-3[2]-4 must return a list, component has sub components")
        self.assertEqual(len(hl7d["PID-3[2]-4"]), 3, "PID-3[2]-4 must return a list with 3 sub components")

        a = hl7d["PID-3[2]-4"]
        a.sort()
        b = ["PID-3[2]-4-1", "PID-3[2]-4-2", "PID-3[2]-4-3"]
        self.assertEqual(a, b, "Error in returned tersers")

    def test_a05(self):
        hl7p = HL7Parser()
        hl7d = hl7p.parse(self.a05)

        self.assertEqual(hl7d["PID-3[1]-1"], "PATID1234", "Error First IPP is PATID1234 in PID-3[1]-1")
        self.assertEqual(hl7d["PID-3[1]-4"], "GOOD HEALTH HOSPITAL",
                          "Error First Assigning Authority is GOOD HEALTH HOSPITAL in PID-3[1]-4")

        self.assertEqual(hl7d["PID-3[2]-1"], "123456789", "Error Second IPP is 123456789 in PID-3[1]-1")
        self.assertEqual(hl7d["PID-3[2]-4"], "USSSA", "Error First Assigning Authority is USSSA in PID-3[1]-4")

if __name__ == '__main__':
    unittest.main()