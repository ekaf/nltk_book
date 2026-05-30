#!/usr/bin/env python
# Post-process latex output in-place

import sys
import re

# load the file
# Note: sys.argv[1] must be a relative CWD path to comply with nltk.pathsec
# sentinel (NLTK >= 3.10). See: https://github.com/nltk/nltk/pull/3522
file = open(sys.argv[1])
contents = file.read()
file.close()

# modify it
contents = re.sub(r'subsection{', r'subsection*{', contents)

# save the file
file= open(sys.argv[1], 'w')
file.write(contents)
file.close()
