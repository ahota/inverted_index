# inverted_index
A Hadoop map-reduce program to generate an inverted index for querying

## Structure

**out/** - Contains output from both WordCount and InvertedIndex map-reduce
functions. The post-processing hadoopOutputToJSON.py script converts the
InvertedIndex output to JSON, which the queryII.py script can read and query
from. The plot.py script allows you to generate a histogram of word count to 
visually inspect the words. This is how we chose our stop word threshold.

**run*** - Bash script to run the entire suite, starting with pre-processing,
then the Hadoop jobs, and ending with post-processing. There are many variables 
for environment-specific parameters that *must be changed* in order to run 
this.

**script/** - Contains the pre-processing script line_number.py, which adds a
document ID and line number to all lines in all .txt files in txt/. It outputs
docs_id.json, which contains the document ID -> filename mapping for
queryII.py.

**src/** - Contains the two Hadoop Java classes, WordCount and InvertedIndex.
WordCount is a slightly modified version of the word count example provided in
Hadoop. InvertedIndex.jar contains both classes and is used by Hadoop for
processing the text.

**txt/** - Contains the source text files from Gutenberg. All .txt files have
their Gutenberg header removed, but are otherwise unaltered. The corresponding
.num files contain document ID and line numbers as added by line_number.py.

## Overview

### Setup
The text files provided by Gutenberg contain differing headers, which are
multiple pages long. These were manually removed so that they don't interfere
with word counting the plays. Additionally, we assumed users won't want to 
query the header of the files. However, there are still additional intermediate
Gutenberg copyright notices that would be difficult to remove. These would have
influenced word count and stop word threshold.

### Pre-processing
We can use the raw text files to get word counts and to determine the stop word
threshold. However for generating the inverted index, we need the document ID
and line number, since lines in files will get separated across datanodes. We
add these in the pre-processing step.

The script/line_number.py executable adds document ID and line number to every 
line in every .txt file in the txt/ directory. The document ID -> filename
mapping is saved as a JSON file so that the results

### Hadoop

### Post-processing

## Running

