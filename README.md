# inverted\_index
A Hadoop map-reduce program to generate an inverted index for querying

## Structure

**out/** - Contains output from both WordCount and InvertedIndex map-reduce
functions. The post-processing hadoopOutputToJSON.py script converts the
InvertedIndex output to JSON, which the queryII.py script can read and query
from. The plot.py script allows you to generate a histogram of word count to 
visually inspect the words. This is how we chose our stop word threshold.

**run**\* - Bash script to run the entire suite, starting with pre-processing,
then the Hadoop jobs, and ending with post-processing. There are many variables 
for environment-specific parameters that *must be changed* in order to run 
this.

**script/** - Contains the pre-processing script line\_number.py, which adds a
document ID and line number to all lines in all .txt files in txt/. It outputs
docs\_id.json, which contains the document ID -> filename mapping for
queryII.py.

**src/** - Contains the two Hadoop Java classes, WordCount and InvertedIndex.
WordCount is a slightly modified version of the word count example provided in
Hadoop. InvertedIndex.jar contains both classes and is used by Hadoop for
processing the text.

**txt/** - Contains the source text files from Gutenberg. All .txt files have
their Gutenberg header removed, but are otherwise unaltered. The corresponding
.num files contain document ID and line numbers as added by line\_number.py.

## Overview

### Setup
The text files provided by Gutenberg contain differing headers, which are
multiple pages long. These were manually removed so that they don't interfere
with word counting the plays. Additionally, we assume users won't want to query 
the header of the files. However, there are still additional intermediate
Gutenberg copyright notices that would be difficult to remove. These would have
influenced word count and stop word threshold.

Currently we have 16 works by Shakespeare that are processed:

### Pre-processing
We can use the raw text files to get word counts and to determine the stop word
threshold. However for generating the inverted index, we need the document ID
and line number, since lines in files will get separated across datanodes. We
add these in the pre-processing step.

The script/line\_number.py executable adds document ID and line number to every 
line in every .txt file in the txt/ directory. These are saved as .num files,
which apart from the ID and line number are identical to their corresponding
.txt file. The document ID -> filename mapping is saved as a JSON file so that
we can print filenames during querying as opposed to IDs.

### Hadoop
There are two Hadoop jobs that can be run. Both are classes included in 
invertedindex.jar in src/.

The first job is WordCount, which simply creates a word frequency table. Our
implementation is a slightly modified  version of the WordCount class provided
with Hadoop. The output of this is essentially a space-delimited CSV file,
which we can then parse with Python. The plot.py script in out/ allows you to
generate a histogram of word counts. We visually analyzed this histogram to
find our stop word threshold of 2000.

<img src="https://raw.githubusercontent.com/ahota/inverted_index/master/out/words.png"
alt="Plot of the 20-50th most frequent words"
width="500px">

The second Hadoop job is InvertedIndex. This computes the inverted index of
words in the corpus using the .num files. Each mapper receives a line. Since
each line contains the document ID and line number as its first two "words",
we can easily determine these two aspects of the offset key for all words in
the line. As the mapper iterates through words in the line, it increments a
current word counter, which is the third element of a word's offset. These
three values are saved as a Hadoop Text object in this format: 
`<doc_id>-<line_num>-<word_num>`.
In the reducing phase, the reducer simply counts the occurrence of incoming
words. If the occurrence is higher than our threshold, it is considered a stop
word and is discarded.

### Post-processing
The output from the Hadoop jobs are text files. During the post-processing
step, the text file output of InvertedIndex is converted to a JSON file. This
greatly simplifies the search when querying.

### Querying
We take the user's query and, for every block that does not contain 'and',
'or', or 'not', we get a query result from the inverted index in form of a set.
Then for each boolean operand in the query, we perform set arithmetic to get a
final result. This required extending the builtin set class' abilities in
Python. We overloaded element equality such that `a = b` returned true if the
word `b` came directly after `a`. The equality is not transitive, meaning if `a
= b`, `b != a`.

## Usage
The simplest way to run the entire project is by modifying the **run**
executable in the project base directory. This requires some setup in the form
of changing the path variables to the correct paths in the running environment.
Once done, the script will run the pre-processing step, both Hadoop jobs, and
the post-processing step. The output from both jobs gets automatically copied
to the local filesystem.

Usage: `run <title>`  
The `<title>` argument is used to store the output of both jobs into unique
directories to compare output between different runs of the project.

To query the inverted index, run query.py. This will bring up an interactive
terminal interface for querying. Simply enter a search query and hit enter. You
will be presented with the results, if any, in a list. Hitting enter on any
item will open Vim at that line.

## Examples
If we query for `romeo and juliet`, we get 8 results:
```
# romeo_and_juliet.txt, line 1
# romeo_and_juliet.txt, line 2562
# romeo_and_juliet.txt, line 2888
# romeo_and_juliet.txt, line 4277
# romeo_and_juliet.txt, line 4327
# romeo_and_juliet.txt, line 4416
# romeo_and_juliet.txt, line 4428
# romeo_and_juliet.txt, line 4430
```

Note that this does not search for "Romeo and Juliet", but only for lines which
contain both "Romeo" and "Juliet". Sorry, hopeless romantics.

If we look at result 4, on line 4277, we can see that both Romeo and Juliet
have died. If this makes you sad, you can instead search for `romeo and juliet
not dead`, and get _6_ results instead:
```
# romeo_and_juliet.txt, line 1
# romeo_and_juliet.txt, line 2562
# romeo_and_juliet.txt, line 2888
# romeo_and_juliet.txt, line 4416
# romeo_and_juliet.txt, line 4428
# romeo_and_juliet.txt, line 4430
```

These results do not contain the lines containing the word `dead`.

An example of consecutive words could be `king lear hath lost`, which returns a
single result:
```
# king_lear.txt, line 3827
```

On this line, we can see that King Lear hath indeed lost.
