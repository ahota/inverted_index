#!/usr/bin/env python

"""
Lyle Scott, III
lyle@digitalfoo.net

A simple demo that uses curses to scroll the terminal.
"""
import curses
import curses.textpad as textpad
import sys
import random
import time
import os
import subprocess
import shlex

def get_query():
    screen = curses.initscr()
    curses.start_color()
    curses.echo()
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
    screen.keypad(1) 
    screen.border(0)
    win = curses.newwin(5, 60, 5, 10)
    win.box()
    screen.refresh()
    win.refresh()
    win.addstr(0, 0, "Please enter a query string: ")
    text = win.getstr(2, 2)
    curses.endwin()
    return text

class MenuDemo:
    DOWN = 1
    UP = -1
    SPACE_KEY = 10 
    ESC_KEY = 27

    PREFIX_SELECTED = '---'
    PREFIX_DESELECTED = '#'

    outputLines = []
    screen = None
            
    def __init__(self, lst):
        self.initialize(lst)

    def initialize(self, lst):
        self.screen = curses.initscr()
        curses.start_color()
        curses.noecho()
        curses.cbreak()
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_WHITE)
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
        self.screen.keypad(1) 
        self.screen.border(1)
        self.topLineNum = 0
        self.highlightLineNum = 0
        self.markedLineNums = []
        self.getOutputLines(lst)
        self.lst = lst
        self.run()

    def run(self):
        exit_menu = False
        while True and not exit_menu:
            self.displayScreen()
            # get user command
            c = self.screen.getch()
            if c == curses.KEY_UP: 
                self.updown(self.UP)
            elif c == curses.KEY_DOWN:
                self.updown(self.DOWN)
            elif c == self.SPACE_KEY:
                self.markLine()
            elif c == self.ESC_KEY:
                exit_menu = True

    def markLine(self):
        curses.def_prog_mode()    # save curent curses environment
        os.system('reset')
        
        linenum = self.topLineNum + self.highlightLineNum
        pair = self.outputLines[linenum].split(",")
        search_line_num = pair[1][pair[1].rfind(" ") + 1:]
        subprocess.call(shlex.split('vim +' + search_line_num + " ../txt/" + pair[0]))
        
        self.screen.clear() 
        curses.reset_prog_mode()   # reset to 'current' curses environment
        curses.curs_set(1)         # reset doesn't do this right
        curses.curs_set(0)

    def getOutputLines(self, lst):
        ### !!!
        ### This is where you would write a function to parse lines into rows 
        ### and columns. For this demo, I'll just create a bunch of random ints
        ### !!!
        self.outputLines = lst
        self.nOutputLines = len(self.outputLines)

    def displayScreen(self):
        # clear screen
        self.screen.clear()

        # now paint the rows
        n_metadeta_lines = 1
        top = self.topLineNum
        bottom = self.topLineNum + curses.LINES - n_metadeta_lines
        for (index,line,) in enumerate(self.outputLines[top:bottom]):
            linenum = self.topLineNum + index
            if linenum in self.markedLineNums:
                prefix = self.PREFIX_SELECTED
            else:
                prefix = self.PREFIX_DESELECTED

            line = '%s %s' % (prefix, line,)

            # highlight current line            
            self.screen.addstr(0, 0, str(len(self.lst)) + " results found, press enter to view and escape to exit.")
            #self.screen.addstr(0, 0, "ENTER: open file in Vim, ESC: exit", curses.color_pair(1))
            if index != self.highlightLineNum:
                self.screen.addstr(index + 1, 0, line)
            else:
                self.screen.addstr(index + 1, 0, line, curses.color_pair(2))
        self.screen.refresh()

    # move highlight up/down one line
    def updown(self, increment):
        nextLineNum = self.highlightLineNum + increment

        # paging
        if increment == self.UP and self.highlightLineNum == 0 and self.topLineNum != 0:
            self.topLineNum += self.UP 
            return
        elif increment == self.DOWN and nextLineNum == curses.LINES-1 and (self.topLineNum+curses.LINES - 1) != self.nOutputLines:
            self.topLineNum += self.DOWN
            return

        # scroll highlight line
        if increment == self.UP and (self.topLineNum != 0 or self.highlightLineNum != 0):
            self.highlightLineNum = nextLineNum
        elif increment == self.DOWN and (self.topLineNum+self.highlightLineNum+0) != self.nOutputLines and self.highlightLineNum != curses.LINES - 2:
            self.highlightLineNum = nextLineNum
 
    def restoreScreen(self):
        curses.initscr()
        curses.nocbreak()
        curses.echo()
        curses.endwin()
    
    # catch any weird termination situations
    def __del__(self):
        self.restoreScreen()

     
#if __name__ == '__main__':
#    ih = MenuDemo()
    
