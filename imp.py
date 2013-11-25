#! /usr/bin/env python
import MySQLdb
import getpass
import readline
import sys
import os
import cmd

global host, user, password, database


class MysqlRequest(object):

    def __init__(self, func):
        self.db = ""
        self.func = func

    def __call__(self, line):
        db = MySQLdb.connect(
            host, user, password, database
        )
        values = self.func(db.cursor(), line)
        db.close()
        return values


class Prompt(cmd.Cmd):
    prompt = ">> "
    tables = []
    to_dir = False

    @MysqlRequest
    def requestTables(cursor, line):
        cursor.execute("SHOW TABLES")
        return [
            table[0] for table in cursor.fetchall()
        ]

    def do_help(self, line):
        print "Commands availables : "
        print 'tables, dump, restore, clear'
        print "count table_name, truncate table_name"

    def do_exit(self, line):
        sys.exit()

    @MysqlRequest
    def do_count(cursor, table):
        try:
            if not table:
                print "table_name needed"
                return
            cursor.execute("SELECT COUNT(*) FROM " + table)
            print cursor.fetchone()[0]
        except MySQLdb.Error as excep:
            print excep.args[1]
            pass

    def do_set_path(self, line):
        if not line:
            print "path not specified"
            return
        self.to_dir = line

    def do_tables(self, line):
        print self.requestTables("")

    # @MysqlRequest
    # def do_truncate(cursor, table):
    #     try:
    #         if not table:
    #             print "table_name needed"
    #             return
    #         cursor.execute("SET foreign_key_checks=0")
    #         value = cursor.execute("SELECT @@foreign_key_checks")
    #         print value
    #         cursor.execute("SET foreign_key_checks=1")
    #     except MySQLdb.Error as excep:
    #         print excep.args[1]
    #         pass

    # def do_restore(self, line):
    #     if not self.to_dir:
    #         self.get_target_dir()

    # def do_dump(self, line):
    #     if self.to_dir is False:
    #         self.get_target_dir()

    def complete_count(self, text, line, start_index, end_index):
        return self.tables_complete(text)

    def complete_truncate(self, text, line, start_index, end_index):
        return self.tables_complete(text)

    def tables_complete(self, text):
        if text:
            return [
                table for table in self.tables
                if table.startswith(text)
            ]
        else:
            return self.tables

    def complete_set_path(self, path, line, start_index, end_index):
        if not path:
            return self.listdir('.')
        dirname, rest = os.path.split(path)
        tmp = dirname if dirname else '.'
        res = [
            p for p in self.listdir(tmp) if p.startswith(rest)
        ]
        # more than one match, or single match which does not exist (typo)
        if len(res) == 1:
            return [
                os.path.join(dirname, p)
                for p in self.listdir(tmp)
                if p.startswith(rest)
            ]

        if len(res) > 1 or not os.path.exists(path):
            return res
        # resolved to a single directory, so return list of files below it
        if os.path.isdir(path):
            return [os.path.join(path, p) for p in self.listdir(path)]
        # exact file match terminates this completion
        return [path + ' ']

    def listdir(self, root):
        res = []
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if os.path.isdir(path):
                name += os.sep
            res.append(name)
        return res


def main():
    global host, user, password, database
    host = "127.0.0.1"
    for arg in sys.argv:
        if '-b=' in arg:
            database = arg[3:]
        if '-u=' in arg:
            user = arg[3:]
        if '-h=' in arg:
            host = arg[3:]

    password = getpass.getpass()
    prompt = Prompt()
    prompt.tables = prompt.requestTables("")
    readline.set_completer_delims(' \t\n;')
    prompt.cmdloop()

if __name__ == '__main__':
    main()
