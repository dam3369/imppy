import MySQLdb
import getpass
import readline
import sys
import os
import cmd
import time
import glob
import getopt


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
        try:
            values = ''
            values = self.func(db.cursor(), line)
        except MySQLdb.Error as excep:
            print excep.args[1]
            pass

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

    @MysqlRequest
    def use(cursor, base):
        cursor.execute("USE `%s`" % (base))

    def do_exit(self, line):
        print ""
        print "Goodbye"
        sys.exit()

    @MysqlRequest
    def do_count(cursor, table):
        try:
            if not table:
                print "table_name needed"
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

    def restore_tables(self):
        path = self.get_lastest_folder()
        preg = path + os.path.sep + '*.sql'
        for table_dump in glob.glob(preg):
            self.restore(table_dump)

    def restore_table(self, table):
        path = self.get_lastest_folder()
        table_dump = path + os.path.sep + table + '.sql'
        self.restore(table_dump)

    def restore(self, dump):
        request = self.get_export_request()
        print "Restoring %s" % dump
        os.system(str(request) + str(dump))

    def get_export_request(self):
        if self.connect.password == "":
            return "mysql -u %s -h %s -b %s < " % (self.connect.user, self.connect.host, self.connect.database)
        else:
            return "mysql -u %s -p%s -h %s -b %s < " % (self.connect.user, self.connect.password, self.connect.host, self.connect.database)

    def get_lastest_folder(self):
        results = []
        root = os.path.join(self.to_dir, self.connect.database)
        for path in os.listdir(root):
            bd = os.path.join(root, path)
            if os.path.isdir(bd):
                results.append(bd)
        return max(results, key=os.path.getmtime)

    def do_dump(self, line):
        path = self.get_path()
        for table in self.tables:
            filepath = os.path.join(path, "%s.sql" % (table))
            request = self.get_dump_request(table, filepath)
            print "Dumping %s" % table
            os.system(str(request))

    def get_dump_request(self, table, path):
        if self.connect.password == "":
            return "mysqldump -u %s -h %s --add-drop-table %s %s --result-file=%s" % (self.connect.user, self.connect.host, self.connect.database, table, path)
        else:
            return "mysqldump -u %s -p%s -h %s  --add-drop-table %s %s --result-file=%s" % (self.connect.user, self.connect.password, self.connect.host, self.connect.database, table, path)

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

    def complete_restore(self, text, line, start_index, end_index):
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


def addslashes(s):
    l = ["\\", '"', "'", "\0", ]
    for i in l:
        if i in s:
            s = s.replace(i, '\\'+i)
    return s


def print_help():
    return 'usage: imppy [--database, -d [database name]] [--user, -u [mysql user]] [--host, -h [host database]] [--help]'


def main():
    global connect
    connect = Connection

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
        prompt = Prompt()
        prompt.connect = connect
        if connect.database:
            prompt.tables = prompt.requestTables("")
        prompt.databases = prompt.requestDatabases("")
        prompt.to_dir = os.path.join(os.path.expanduser("~"), "imppy-dump")
        readline.set_completer_delims(' \t\n;')
        prompt.cmdloop("Welcome")
    except KeyboardInterrupt:
        print ""
        print "Goodbye"
