===================
HL7 Tersely Library
===================

Description
-----------

These library parse HL7 messages and produces dictionaries.
It's easy to use and straightforward.

Install
-------

Install from pypi (https://pypi.python.org/pypi)

    pip install hl7tersely

Start playing
-------------

.. code-block:: pycon

    # load HL7 data into hl7message

    >>> from hl7tersely import HL7Parser
    >>> hl7p = HL7Parser()
    >>> myhl7dict = hl7p.parse(hl7message)
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


MIT Licensed