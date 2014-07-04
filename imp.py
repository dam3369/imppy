#! /usr/bin/env python
# -*- coding: utf-8 -*-

import getpass
import readline
import sys
import os
import getopt
from Prompt.Cmd import Cmd
from Connection import Connection

def addslashes(s):
    l = ["\\", '"', "'", "\0", ]
    for i in l:
        if i in s:
            s = s.replace(i, '\\'+i)
    return s


def print_help():
    return 'usage: imppy [--database, -d [database name]] [--user, -u [mysql user]] [--host, -h [host database]] [--help]'


def main():
    connect = Connection()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:u:h:", ["help", "database=", "user=", "host="])
    except getopt.GetoptError:
        print print_help()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '--help':
            print print_help()
            sys.exit()
        elif opt in ('-d', '--database'):
            connect.database = arg
        elif opt in ('-u', '--user'):
            connect.user = arg
        elif opt in ('-h', '--host'):
            connect.host = arg

    try:
        connect.password = getpass.getpass()
        prompt = Cmd()
        if connect.database:
            prompt.tables = prompt.requestTables("")
        prompt.databases = prompt.requestDatabases("")
        prompt.to_dir = os.path.join(os.path.expanduser("~"), "imppy-dump")
        readline.set_completer_delims(' \t\n;')
        prompt.cmdloop("Welcome")
    except KeyboardInterrupt:
        print ""
        print "Goodbye"

if __name__ == '__main__':
    main()
