#!/usr/bin/python

import sys
import json
import pprint
import collections
import re
#import menu_launcher
#from menu_launcher import *
import curses_menu
from curses_menu import *

class Address(object):
    def __init__(self, obj):
        self.obj = obj

    def __eq__(self, other):
        parts = self.obj.split("-")
        other_parts = other.obj.split("-")
        are_equal = (parts[0] == other_parts[0]) and (parts[1] == other_parts[1]) and (int(parts[2]) == int(other_parts[2]) - 1)
        return are_equal
    
    def __hash__(self):
        parts = self.obj.split("-")
        return hash(parts[0] + "-" + parts[1])

    def get(self):
        return self.obj

def print_set(s):
    l = list(s)
    for x in l:
        if type(x) is Address:
            print x.obj
        else:
            print x

def intersect(l, r):
    res = set()
    r_list = list(r)
    for item in r_list:
        if item in l:
            res.add(item)

    return res

def add(s, item):
    l = list(s)
    for x in l:
        if x.obj == item.obj:
            return
    s.add(item)

def eval_pack(ii, str):
    words = str.split()
    line_num = -1
    first_search = 1
    running_set = set()
    for word in words:
        if word not in ii:
            return set()
        word_res = ii[word]
        one_word_set = set()
        for res in word_res:
            add(one_word_set, Address(res))

        if first_search == 1:
            running_set = running_set.union(one_word_set)
        else:
            running_set = intersect(running_set, one_word_set)
        first_search = 0

    l = list(running_set)
    result = set()
    for x in l:
        result.add(x.obj[:x.obj.rfind("-")])

    return result

def word_to_var(word):
    var = "VAR_NAME_" + word.strip().replace(" ", "_")
    var = re.sub(r'[^\w]', '_', var)
    return var

# This is totaly crazy but it works!!
def search(ii, query):
    query = query.replace(" and ", " & ")
    query = query.replace(" or ", " | ")
    query = query.replace(" not ", " - ")
    q_items = re.split("&|\||-", query)
    for item in q_items:
        var = word_to_var(item)
        query = query.replace(item, var)
        exec(var + "=eval_pack(ii, item)")

    return eval(query)

docs = json.load(open('doc_ids.json'))
ii = json.load(open('inverted_index.json'))
query_text = get_query()
results = search(ii, query_text)
if len(results) == 0:
    print "Nothing found."
else:
    post_proc = []
    for x in results:
        pair = x.split("-")
        line_num = str(int(pair[1])+1)
        post_proc.append(docs[pair[0]] + ", line " + line_num)
  
    MenuDemo(sorted(post_proc))
    curses.endwin() 
    os.system('clear')

