#! /usr/bin/env python
import MySQLdb
import getpass
import readline
import sys
import os
import cmd
import time
import glob
import subprocess


class Connection(object):
    host = "127.0.0.1"
    user = "root"
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
        self.tables = self.requestTables("")
        print self.tables

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

    def do_restore(self, line):
        self.drop_tables()
        path = self.get_lastest_folder()
        preg = path + os.path.sep + '*.sql'
        request = self.get_export_request()
        for table_dump in glob.glob(preg):
            print str(request) + '"' + str(table_dump) + '"'
            os.system(str(request) + str(table_dump))

    def get_export_request(self):
        if self.connect.password == "":
            return "mysql -u %s -h %s -b %s < " % (self.connect.user, self.connect.host, self.connect.database)
        else:
            return "mysql -u %s -p%s -h %s -b %s < " % (self.connect.user, self.connect.password, self.connect.host, self.connect.database)

    @MysqlRequest
    def restore_table(cursor, filename):
        for line in open(filename, "r"):
            if line != "":
                cursor.execute(line)

    def get_lastest_folder(self):
        results = []
        root = os.path.join(self.to_dir, self.connect.database)
        for path in os.listdir(root):
            bd = os.path.join(root, path)
            if os.path.isdir(bd):
                results.append(bd)
        return max(results, key=os.path.getmtime)

    def drop_tables(self):
        for table in self.tables:
            self.drop_table(table)

    @MysqlRequest
    def drop_table(cursor, table):
        cursor.execute("SET foreign_key_checks = 0;")
        cursor.execute("DROP TABLE %s;" % (table))
        cursor.execute("SET foreign_key_checks = 1;")

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
        data = "SET foreign_key_checks = 0;\n"
        data += "DROP TABLE IF EXISTS `" + str(table) + "`;\n"

        cursor.execute("SHOW CREATE TABLE `" + str(table) + "`;")
        data += str(cursor.fetchone()[1]) + ";\n"

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
        data += "SET foreign_key_checks = 1;\n"
        return data

    def get_path(self):
        if self.to_dir is False:
            self.get_target_dir()

        if not os.path.exists(self.to_dir):
            os.makedirs(self.to_dir)

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
        if len(res) == 1:
            return [
                os.path.join(dirname, p)
                for p in self.listdir(tmp)
                if p.startswith(rest)
            ]

        if len(res) > 1 or not os.path.exists(path):
            return res
        if os.path.isdir(path):
            return [os.path.join(path, p) for p in self.listdir(path)]
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
    prompt.to_dir = os.path.join(os.path.expanduser("~"), "imppy-dump")
    readline.set_completer_delims(' \t\n;')
    prompt.cmdloop()

if __name__ == '__main__':
    main()
