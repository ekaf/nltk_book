#!/usr/bin/env python
#
# Natural Language Toolkit: Page length extraction script
#
# Copyright (C) 2001-2006 NLTK Project
# Author: Steven Bird <sb@csse.unimelb.edu.au>
# URL: <http://www.nltk.org/>
# For license information, see LICENSE.TXT

r"""

This script extracts the pagecount from a latex log file.

"""

import re
import sys

# Note: Under nltk.pathsec (NLTK >= 3.10), file paths must reside within
# the current working directory or an authorized nltk.data.path root.
# See: https://github.com/nltk/nltk/pull/3522

regexp = r'\[(\d+)\][^\[]*$'       # last [nn] in file
logfile = open(sys.argv[1]).read()  # latex logfile
print(re.search(regexp, logfile).group(1))
