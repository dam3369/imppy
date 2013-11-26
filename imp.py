#! /usr/bin/env python
import MySQLdb
import getpass
import readline
import sys
import os
import cmd
import time


class Connection(object):
    host = "127.0.0.1"
    user = ""
    password = ""
    database = ""


class MysqlRequest(object):

    def __init__(self, func):
        self.db = ""
        self.func = func

    def __call__(self, line):
        db = MySQLdb.connect(
            connect.host, connect.user, connect.password, connect.database
        )
        values = self.func(db.cursor(), line)
        db.close()
        return values


class Prompt(cmd.Cmd):
    prompt = ">> "
    tables = []
    databases = []
    to_dir = False
    connect = ""

    @MysqlRequest
    def requestTables(cursor, line):
        cursor.execute("SHOW TABLES")
        return [
            table[0] for table in cursor.fetchall()
        ]

    @MysqlRequest
    def requestDatabases(cursor, line):
        cursor.execute("SHOW DATABASES")
        return [
            data[0] for data in cursor.fetchall()
        ]

    def do_help(self, line):
        print "Commands availables : "
        print 'tables, dump, restore, clear'
        print "count table_name, truncate table_name"

    def do_use(self, base):
        self.connect.database = base
        self.tables = self.requestTables("")
        self.use(base)

    @MysqlRequest
    def use(cursor, base):
        cursor.execute("USE %s" % (base))

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

    def do_dump(self, line):
        path = self.get_path()
        for table in self.tables:
            filepath = os.path.join(path, "%s.sql" % (table))
            content = self.dump_table(table)
            dump = open(filepath, "w")
            dump.writelines(content)
            dump.close()

    @MysqlRequest
    def dump_table(cursor, table):
        data = "DROP TABLE IF EXISTS `" + str(table) + "`;"

        cursor.execute("SHOW CREATE TABLE `" + str(table) + "`;")
        data += "\n" + str(cursor.fetchone()[1]) + ";\n\n"

        cursor.execute("SELECT * FROM `" + str(table) + "`;")
        for row in cursor.fetchall():
            data += "INSERT INTO `" + str(table) + "` VALUES("
            first = True
            for field in row:
                if not first:
                    data += ', '
                data += '"' + str(field) + '"'
                first = False

            data += ");\n"
        data += "\n\n"
        return data

    def get_path(self):
        if self.to_dir is False:
            self.get_target_dir()

        root = os.path.join(self.to_dir, self.connect.database)
        if not os.path.exists(root):
            os.makedirs(root)

        filename = os.path.join(root, "imppy-%d" % (int(time.time())))
        if not os.path.exists(filename):
            os.makedirs(filename)
        return filename

    def complete_use(self, text, line, start_index, end_index):
        if text:
            return [
                data for data in self.databases
                if data.startswith(text)
            ]
        else:
            return self.databases

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
    global connect
    connect = Connection
    for arg in sys.argv:
        if '-b=' in arg:
            connect.database = arg[3:]
        if '-u=' in arg:
            connect.user = arg[3:]
        if '-h=' in arg:
            connect.host = arg[3:]

    connect.password = getpass.getpass()
    prompt = Prompt()
    prompt.connect = connect
    prompt.tables = prompt.requestTables("")
    prompt.databases = prompt.requestDatabases("")
    readline.set_completer_delims(' \t\n;')
    prompt.cmdloop()

if __name__ == '__main__':
    main()
