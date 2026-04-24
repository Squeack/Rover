#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import curses

STARTMENU = "top.menu"
MENUSCRROW = 18
DESCCOL = 30
SCREENSAVER = 30000  # milliseconds
menu = {}
menuline = 0
menustack = []
cmdoutput = None


def splitatcolon(s):
    sp = s.split(":")
    s1 = sp[0].strip()
    s2 = ":".join(sp[1:]).strip()
    return s1, s2


def loadMenu(mname):
    global menu
    global menuline
    menu.clear()
    lastmenu = ""
    if len(menustack) > 0:
        lastmenu = menustack[-1]
    if mname != lastmenu:
        menustack.append(mname)
    fmenu=open(mname)
    for mline in fmenu:
        k,v = splitatcolon(mline)
        menu[k] = v
    menuline = 0


def externalCmd(scr,command):
    # Close down curses
    curses.nocbreak();
    scr.keypad(False)
    curses.echo()
    curses.endwin()
    # Run command
    os.system(command)
    # Reestablish curses
    scr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    scr.keypad(True)

def showOutput(scr, lines):
    if lines is None:
        return()
    lines = lines.split("\n")
    startline = len(lines) + 1 - MENUSCRROW
    if startline < 0:
        startline = 0
    scrline = 0
    for line in lines[startline:]:
        scr.addstr(scrline,0,line)
        scrline += 1

def executeMenu(scr):
    global menu
    global menuline
    global menustack
    global cmdoutput
    option = list(menu.keys())[menuline]
    todo = menu[option]
    style,command = splitatcolon(todo)
    style = style.lower()
    if style == "menu":
        loadMenu(command)
        return()
    if style == "backmenu":
        backMenu()
        return()
    if style == "cmd":
        runcmd = os.popen(command)
        cmdoutput = runcmd.read()
        showOutput(scr, cmdoutput)
        return()
    if style == "extcmd":
        externalCmd(scr, command)


def backMenu():
    global menustack
    if len(menustack) > 1:
        prevmenu = menustack[-2]
        menustack.pop()
        loadMenu(prevmenu)


def refreshScreens(scrlist):
    for s in scrlist:
        s.nooutrefresh()
        curses.doupdate()


def showMenu(scr):
    minlimit = 0
    maxlimit = len(menu) - 1
    # Start with a +-2 range
    startline = menuline - 2
    endline = menuline + 2
    # Limit to menu size
    startline = max(startline, minlimit)
    endline = min(endline, maxlimit)
    # Expand one way if near the other end
    endline = min(startline + 4, maxlimit)
    startline = max(endline - 4, minlimit)
    scrline = 0
    for n in range(startline, endline+1):
        menuk = list(menu.keys())[n]
        if n == menuline:
            scr.addstr(MENUSCRROW + scrline, 0, "*> {}".format(menuk), curses.A_STANDOUT)
        else:
            scr.addstr(MENUSCRROW + scrline, 0, "*  {}".format(menuk))
        scrline += 1


def showMenuStack(scr):
    global menustack
    rows, cols = scr.getmaxyx()
    stack=""
    for m in menustack:
        stack += ":" + m.split('.')[0]
    scr.addstr(rows-1, 0, stack, curses.A_REVERSE)

def main(stdscr):
    global menu
    global menuline
    global cmdoutput
    global MENUSCRROW
    loadMenu(STARTMENU)
    rows, cols = stdscr.getmaxyx()
    MENUSCRROW = rows - 6
    c = 0
    while c != ord('q'):
        stdscr.clear()
        showOutput(stdscr, cmdoutput)
        showMenu(stdscr)
        showMenuStack(stdscr)

        stdscr.refresh()
        stdscr.timeout(SCREENSAVER)
        c = stdscr.getch()
        if c == ord('u') or c == curses.KEY_UP:
            menuline -= 1
        if c == ord('d') or c == curses.KEY_DOWN:
            menuline += 1
        if menuline < 0:
            menuline = 0
        if menuline >= len(menu):
            menuline = len(menu) - 1
        if c == ord('r') or c == curses.KEY_RIGHT:
            executeMenu(stdscr)
        if c == ord('l') or c == curses.KEY_LEFT:
            backMenu()
        if c == curses.ERR:
            # Screen saver mode
            stdscr.clear()
            # until a key is pressed
            stdscr.timeout(-1)
            c = stdscr.getch()

curses.wrapper(main)
