import MySQLdb
from Connection import Connection

class MysqlRequest(object):

    def __init__(self, func):
        self.db = ""
        self.func = func
        self.connect = Connection()

    def __call__(self, line):
        connect = Connection()
        db = MySQLdb.connect(
            host=self.connect.host, user=self.connect.user, passwd=self.connect.password, db=self.connect.database, use_unicode="True", charset="utf8"
        )
        try:
            values = ''
            values = self.func(db.cursor(), line)
        except MySQLdb.Error as excep:
            print excep.args[1]
            pass

        db.close()
        return values

class MysqlProtectedRequest(object):

    def __init__(self, func):
        self.db = ""
        self.func = func
        self.connect = Connection()

    def __call__(self, line):
        db = MySQLdb.connect(
            host=self.connect.host, user=self.connect.user, passwd=self.connect.password, db=self.connect.database, use_unicode="True", charset="utf8"
        )
        db.autocommit(0)
        cursor = db.cursor()
        cursor.execute('FLUSH TABLES WITH READ LOCK;')
        db.commit()
        try:
            done = True
            self.func(cursor, line)
            db.commit()
        except MySQLdb.Error as excep:
            print excep.args[1]
            done = False;
            db.rollback()
            pass

        db.autocommit(1)
        cursor.execute('UNLOCK TABLES;')
        db.close()
        return done