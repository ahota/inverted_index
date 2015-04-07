#!/usr/bin/python

import sys
import json
import pprint

ii = json.load(open(sys.argv[1]))
results = ii[sys.argv[2]]
for result in results:
    pair = result.split("-")
    print "Document " + pair[0] + ", line " + pair[1]
