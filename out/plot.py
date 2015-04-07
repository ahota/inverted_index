#!/usr/bin/env python

import csv, operator, argparse
from matplotlib import pyplot

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--noshow', help='do not show the figure',
        action='store_true', default=False)
parser.add_argument('-t', '--top', type=int,
        help='restrict the top end of the plot', default=0)
parser.add_argument('-b', '--bottom', type=int,
        help='restrict the bottom end of the plot', default=20)
plot_args = parser.parse_args()

print 'Creating figure'

pyplot.figure(figsize=(12, 9), facecolor='white')
axes = pyplot.subplot(111)

axes.spines['top'].set_visible(False)
axes.spines['bottom'].set_visible(False)
axes.spines['right'].set_visible(False)
axes.spines['left'].set_visible(False)

axes.get_xaxis().tick_bottom()
axes.get_yaxis().tick_left()

data = []
words  = []
counts = []

print 'Reading data'

with open('word_count.txt', 'rb') as f:
    wc_reader = csv.reader(f, delimiter='\t')
    for row in wc_reader:
        data.append( (row[0], int(row[1])) )

print 'Removing UTF-8 characters'

for i, val in enumerate(data):
    replacement = ''.join([c for c in val[0] if 0 < ord(c) < 128])
    data[i] = (replacement, val[1])

print 'Sorting and truncating data list'

data.sort(key=operator.itemgetter(1))
#reverse and only look at top words
data = data[::-1]
#the first value ends up being whitespace
data = data[1::]

data = data[plot_args.top:plot_args.bottom]

max_val = max([val[1] for val in data])
print max_val

delta = 500

range_max = delta * (max_val/delta + 1)

pyplot.xlim(-1, len(data))

for y in range(delta, range_max + 1, delta):
    pyplot.plot(range(-1, len(data)+1), [y] * (len(data)+2), '--',
            lw = 0.5, color='black', alpha = 0.3)
pyplot.tick_params(axis='both', which='both', bottom='off',
        top='off', left='off', right='off')
print 'Plotting'

bar_color = (70/255., 137/255., 102/255.)

num = len(data)
width = 0.1
axes.bar(range(num), [val[1] for val in data], color=bar_color)

axes.set_yticks(range(delta, range_max + 1, delta))
axes.set_xticks(range(num))
axes.set_xticklabels([val[0] for val in data], rotation=40, ha='center')

print 'Saving and displaying'

fig = pyplot.gcf()
fig.savefig('words.png', bbox_inches='tight')
if(not plot_args.noshow):
    pyplot.show()
