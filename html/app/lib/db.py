__author__="kayapo"
__date__ ="$2011.02.14. 10:00:24$"

import MySQLdb
import sys
sys.path.append("./")

from log import *

class db():
    """
    Database connection class
    hostname = str(), username = str(), password = str(), databes = str()
    are input parameters
    """

    hostname = str()
    username = str()
    password = str()
    database = str()

    def __init__(self, host, user, passwd, database):
        """Initiate database connection parameters"""

        self.hostname = host
        self.username = user
        self.password = passwd
        self.database = database

    def __del__(self):
        """destructor"""

        return

    def connector(self):
        """Create and return mysql connector object"""

        try:
            conn = MySQLdb.connect(host = self.hostname, user = self.username, passwd = self.password, db = self.database)
        except MySQLdb.Error, e:
            message = "Error in db.connector(): %d, %s" % (e.args[0], e.args[1])
            mLog = log(0,7,"logwalker.lib.db.connector")
            mLog.logger(message)
            return -1
        else:
            return conn

    def runQuery(self, connect, querry):
        """Run MySQL querry on selected database"""

        try:
            cursor = connect.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(querry)
            resoult_set = cursor.fetchall()
        except MySQLdb.Error, e:
            message = "Error in db.runQuery(): %d, %s" % (e.args[0], e.args[1])
            mLog = log(0,7,"logwalker.lib.db.connector")
            mLog.logger(message)
            return -1
        else:
            return resoult_set
