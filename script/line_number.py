#!/usr/bin/env python

import glob, json


def convert_name(filename):
    return filename.replace('.txt', '.num')

text_loc = '/home/ahota/workspace/inverted_index/txt/'

filenames = glob.glob(text_loc + '*.txt')
filenames = [f.split('/')[-1:][0] for f in filenames]
outfiles  = [convert_name(f) for f in filenames]
doc_id = 0
doc_dict = {}

for infile,outfile in zip(filenames, outfiles):
    with open(text_loc+infile, 'rb') as f, open(text_loc+outfile, 'wb') as o:
        line_num = 0
        for line in f.readlines():
            o.write(str(doc_id) + ' ' + str(line_num) + ' ' + line)
            line_num += 1
    print infile, '->', doc_id
    doc_dict[doc_id] = infile
    doc_id += 1

with open('doc_ids.json', 'wb') as doc_json:
    json.dump(doc_dict, doc_json)

print 'Done.'
