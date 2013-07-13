from distutils.core import setup


LONG_DESCRIPTION = """
Parser for HL7 messages. See http://www.hl7.org

The parser delivers a dictionary. The keys are the HL7 terser expressions,
and the value are the values in the message designed by the terser.
Example : Patient Identifier is accessible by a simple access
like hl7dict["PID-3-1"] if hl7dict is the result of the parsing.

Released under MIT Licence.
"""

setup(
    name='hl7tersely',
    version='1.0',
    packages=['hl7tersely'],
    test_suite='hl7tersely.test',
    url='http://github.com/flrt/hl7tersely',
    license='MIT',
    keywords="HL7,hl7,terser",
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',
        'Topic :: Communications',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    author='Frederic Laurent',
    author_email='',

    description='Lightweight HL7 parser focused on HL7 tersers',
    long_description=LONG_DESCRIPTION
)
