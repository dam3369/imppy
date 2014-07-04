from PromptHelp import PromptHelp
from MysqlDecorator import *
from Connection import Connection
import sys
import os
import time
import glob

class Prompt(PromptHelp):
    prompt = ">> "
    tables = []
    databases = []
    to_dir = False
    connect = Connection()

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
        self.lock_database
        for table in self.tables:
            filepath = os.path.join(path, "%s.sql" % (table))
            request = self.get_dump_request(table, filepath)
            print "Dumping %s" % table
            os.system(str(request))
        self.unlock_database

    @MysqlRequest
    def lock_database(cursor, line):
        cursor.execute('FLUSH TABLES WITH READ LOCK;')

    @MysqlRequest
    def unlock_database(cursor, line):
        cursor.execute('UNLOCK TABLES;')

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

    def listdir(self, root):
        res = []
        for name in os.listdir(root):
            path = os.path.join(root, name)
            if os.path.isdir(path):
                name += os.sep
            res.append(name)
        return res