class Connection(object):
    host = "127.0.0.1"
    user = "root"
    password = ""
    database = ""
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Connection, cls).__new__(cls, *args, **kwargs)

        return cls._instance
