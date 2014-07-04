# -*- coding: utf-8 -*-

from Complete import Complete
from MysqlDecorator import *
from Connection import Connection
# from Encoding import Encoding
import sys
import os
import string

class Cmd(Complete):

    def do_help(self, line):
        print "Commands availables :"
        print '- tables : "Show tables"'
        print '- dump : "dump database"'
        print '- restore <optional table> : "restore the last database or table dump"'
        print '- count <table> : "count the table entries"'
        print '- truncate <table> : "remove all table entries"'
        print '- set_path <path> : "change the imppy work folder destination'

    def do_use(self, base):
        self.connect.database = base
        self.use(base)

    def do_exit(self, line):
        print ""
        print "Goodbye"
        sys.exit()

    @MysqlRequest
    def do_count(cursor, table):
        try:
            if not table:
                print "table needed"
                return
            cursor.execute("SELECT COUNT(*) FROM `%s`" % table)
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
        self.tables = self.requestTables("")
        print self.tables

    @MysqlRequest
    def do_truncate(cursor, table):
        try:
            if not table:
                print "table_name needed"
                return
            cursor.execute("SET foreign_key_checks=0")
            cursor.execute("TRUNCATE TABLE `%s`;" % (table))
            cursor.execute("SET foreign_key_checks=1")
        except MySQLdb.Error as excep:
            print excep.args[1]
            pass

    def do_restore(self, line):
        if not line:
            self.restore_tables()
        else:
            self.restore_table(line)

    def do_dump(self, line):
        path = self.get_path()
        self.lock_database
        for table in self.tables:
            filepath = os.path.join(path, "%s.sql" % (table))
            request = self.get_dump_request(table, filepath)
            print "Dumping %s" % table
            os.system(str(request))
        self.unlock_database

    def do_clean(self, line):
        array = line.split(' ')
        if len(array) != 2:
            print 'table and column needed'
            return
        table = array[0]
        column = array[1]
        try:
            contents = self.getContents(talbe, column)
            self.cleanContents(contents)
        except MySQLdb.Error as excep:
            print excep.args[1]
            pass
