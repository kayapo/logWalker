#!/usr/bin/env python

import unittest

import random
import string
import time

import sys
sys.path.append("../html/app/lib/")
sys.path.append("../html/conf/")

from log import LOG
from db import DB
from config import Config
from jsonify import JSONify

class  LOGTestCase(unittest.TestCase):
    def setUp(self):
        self.logObj = LOG(0,0,"syslogTestCase.python.logwalker")
        self.logStamp = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(8))

    def test_logger(self):
        self.logObj.logger("Test log message: " + self.logStamp)
        self.assertEqual(self.grepLog(), 1, "Send a log message to syslog failed!")

    def grepLog(self):
        import re
        ret = 0
        pattern = re.compile("Test log message: " + self.logStamp)
        for line in open("/var/log/syslog", "r"):
            if pattern.search(line):
                ret = 1
        return ret

class DBTestCase(unittest.TestCase):
    def setUp(self):
        self.dbObj = DB(Config.MySQLconnector["host"], Config.MySQLconnector["user"], Config.MySQLconnector["password"], "information_schema")

    def test_connector(self):
        self.assertEqual(type(self.dbObj.connector()).__name__, 'Connection', "MySQL DB connection not created")

    def test_runQuerry(self):
        c = self.dbObj.connector()
        r = self.dbObj.runQuerry(c, "SELECT 'bar' AS foo;")
        self.assertEquals(r[0]['foo'], 'bar', "MySQL DB querry failed")

class JSONifyTestCase(unittest.TestCase):
    def setUp(self):
        self.jsonObj = JSONify()

    def test_objectToSQL(self):
        tObj = {"facility":['auth', 'authpriv'],
                "includeFacility":"include",
                "priority":['debug', 'info', 'notice'],
                "includePriority":"include",
                "hosts":['www', 'mail'],
                "includeHosts":"include",
                "tags":['ssh', 'getty'],
                "includeTags":"include",
                "message":"loged in",
                "includeMessage":"include",
                "before":"2011-02-01 10:00:00",
                "after":"2011-01-01 10:00:00","page":"50"}

        querry = self.jsonObj.objectToSQL(tObj)
        sql = "SELECT id, concat(datetime) AS datetime, host, facility, priority, tag, message, MATCH(`message`) AGAINST('loged in' IN BOOLEAN MODE) AS score FROM logs WHERE `facility` IN('auth', 'authpriv') AND `priority` IN('debug', 'info', 'notice') AND `host` IN('www', 'mail') AND `tag` IN('ssh', 'getty') AND MATCH(`message`) AGAINST('loged in' IN BOOLEAN MODE) ORDER BY score DESC, id DESC LIMIT 50;"

        self.assertEquals(querry, sql, "SQL querry cretion with objectToSQL failed!")

    def test_validityCheckClean(self):
        tObj = {"facility":['auth', 'authpriv'],
                "includeFacility":"include",
                "priority":['debug', 'info', 'notice'],
                "includePriority":"include",
                "includeHosts":"include",
                "includeTags":"include",
                "message":"loged in",
                "includeMessage":"include",
                "before":"2011-02-01 10:00:00",
                "after":"2011-01-01 10:00:00",
                "page":"50"}
        qObj = self.jsonObj.validityCheck(tObj)

        self.assertTrue(set(tObj).intersection(set(qObj)), "JSON object validity clean check failed!")

    def test_validityCheckUnCleanFacility(self):
        tObj = {"facility":['auth', 'authpriv', 'UNCLEAN'],
                "includeFacility":"include",
                "priority":['debug', 'info', 'notice'],
                "includePriority":"include",
                "includeHosts":"include",
                "includeTags":"include",
                "message":"loged in",
                "includeMessage":"include",
                "before":"2011-02-01 10:00:00",
                "after":"2011-01-01 10:00:00",
                "page":"50"}

        rObj = {"facility":['auth', 'authpriv'],
                "includeFacility":"include",
                "priority":['debug', 'info', 'notice'],
                "includePriority":"include",
                "includeHosts":"include",
                "includeTags":"include",
                "message":"loged in",
                "includeMessage":"include",
                "before":"2011-02-01 10:00:00",
                "after":"2011-01-01 10:00:00",
                "page":"50"}

        qObj = self.jsonObj.validityCheck(tObj)

        self.assertTrue(set(rObj).intersection(set(qObj)), "JSON object validity unclean facility check failed!")

    def test_validityCheckUnCleanPriority(self):
        tObj = {"facility":['auth', 'authpriv'],
                "includeFacility":"include",
                "priority":['debug', 'info', 'notice', 'UNCLEAN'],
                "includePriority":"include",
                "includeHosts":"include",
                "includeTags":"include",
                "message":"loged in",
                "includeMessage":"include",
                "before":"2011-02-01 10:00:00",
                "after":"2011-01-01 10:00:00",
                "page":"50"}

        rObj = {"facility":['auth', 'authpriv'],
                "includeFacility":"include",
                "priority":['debug', 'info', 'notice'],
                "includePriority":"include",
                "includeHosts":"include",
                "includeTags":"include",
                "message":"loged in",
                "includeMessage":"include",
                "before":"2011-02-01 10:00:00",
                "after":"2011-01-01 10:00:00",
                "page":"50"}

        qObj = self.jsonObj.validityCheck(tObj)

        self.assertTrue(set(rObj).intersection(set(qObj)), "JSON object validity unclean priority check failed!")

    def test_validityCheckUnCleanIncludePriority(self):
        tObj = {"facility":['auth', 'authpriv'],
                "includeFacility":"include",
                "priority":['debug', 'info', 'notice'],
                "includePriority":"UNCLEAN",
                "includeHosts":"include",
                "includeTags":"include",
                "message":"loged in",
                "includeMessage":"include",
                "before":"2011-02-01 10:00:00",
                "after":"2011-01-01 10:00:00",
                "page":"50"}

        rObj = {"facility":['auth', 'authpriv'],
                "includeFacility":"include",
                "priority":['debug', 'info', 'notice'],
                "includePriority":"include",
                "includeHosts":"include",
                "includeTags":"include",
                "message":"loged in",
                "includeMessage":"include",
                "before":"2011-02-01 10:00:00",
                "after":"2011-01-01 10:00:00",
                "page":"50"}

        qObj = self.jsonObj.validityCheck(tObj)

        self.assertTrue(set(rObj).intersection(set(qObj)), "JSON object validity unclean priority check failed!")

    def test_validityCheckUnCleanBefore(self):
        tObj = {"facility":['auth', 'authpriv'],
                "includeFacility":"include",
                "priority":['debug', 'info', 'notice'],
                "includePriority":"include",
                "includeHosts":"include",
                "includeTags":"include",
                "message":"loged in",
                "includeMessage":"include",
                "before":"UNCLEAN",
                "after":"2011-01-01 10:00:00",
                "page":"50"}

        rObj = {"facility":['auth', 'authpriv'],
                "includeFacility":"include",
                "priority":['debug', 'info', 'notice'],
                "includePriority":"include",
                "includeHosts":"include",
                "includeTags":"include",
                "message":"loged in",
                "includeMessage":"include",
                "before":(time.strftime('%Y-%m-%d %H:%M:%S')),
                "after":"2011-01-01 10:00:00",
                "page":"50"}

        qObj = self.jsonObj.validityCheck(tObj)

        self.assertTrue(set(rObj).intersection(set(qObj)), "JSON object validity unclean before check failed!")

    def test_validityCheckUnCleanAfter(self):
        tObj = {"facility":['auth', 'authpriv'],
                "includeFacility":"include",
                "priority":['debug', 'info', 'notice'],
                "includePriority":"include",
                "includeHosts":"include",
                "includeTags":"include",
                "message":"loged in",
                "includeMessage":"include",
                "before":"2011-02-01 10:00:00",
                "after":"UNCLEAN",
                "page":"50"}

        rObj = {"facility":['auth', 'authpriv'],
                "includeFacility":"include",
                "priority":['debug', 'info', 'notice'],
                "includePriority":"include",
                "includeHosts":"include",
                "includeTags":"include",
                "message":"loged in",
                "includeMessage":"include",
                "before":"2011-02-01 10:00:00",
                "after":"1970:01:01 00:00:00",
                "page":"50"}

        qObj = self.jsonObj.validityCheck(tObj)

        self.assertTrue(set(rObj).intersection(set(qObj)), "JSON object validity unclean after check failed!")

if __name__ == '__main__':
    unittest.main()

