#!/usr/bin/python

import sys
import json

f = open(sys.argv[1])
output = dict()
for line in f:
    pair = line.split()
    if len(pair) > 1:
        if pair[0] in output:
            output[pair[0]].append(pair[1])
        else:
            output[pair[0]] = [pair[1]]

json.dump(output, open(sys.argv[2], 'w'))
print "Done."

