#!/usr/bin/env python
# Pre-process rst source

from optparse import OptionParser
import re

_SCALE_RE = b'(:scale:\s+)(\d+):(\d+):(\d+)'

def process(file, format):
    # Note: 'file' must be a relative CWD path to comply with nltk.pathsec
    # sentinel (NLTK >= 3.10). See: https://github.com/nltk/nltk/pull/3522
    contents = open(file, 'rb').read()
    if format == "html":
        contents = re.sub(_SCALE_RE, r'\1\2', contents)
    elif format == "latex":
        contents = re.sub(_SCALE_RE, r'\1\3', contents)
    elif format == "xml":
        contents = re.sub(_SCALE_RE, r'\1\4', contents)
    open(file + "2", 'wb').write(contents)

parser = OptionParser()
parser.add_option("-f", "--format", dest="format",
                      help="output format (html, latex, xml)", metavar="FMT")

o, a = parser.parse_args()

if o.format and o.format in ["html", "latex", "xml"] and a and len(a) == 1:
    process(a[0], o.format)

else:
    exit("Must specify a format (html, latex, xml) and a filename")
