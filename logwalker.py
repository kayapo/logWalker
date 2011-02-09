#!/usr/bin/env python
__author__="kayapo"
__date__ ="$2011.02.04. 18:18:33$"

import sys
import MySQLdb
import syslog
import json
import cgi

sys.path.append("./")
from config import Config

class LOG():
    def logger(self, msg):
        syslog.openlog('logWalker', 0, 23)
        syslog.syslog(3, msg)
        syslog.closelog()

class DB:

    def connector(self, database):
        try:
            self.conn = MySQLdb.connect(host = Config.MySQLconnector['host'], user = Config.MySQLconnector['user'], passwd = Config.MySQLconnector['password'], db = database)
        except MySQLdb.Error, e:
            message = "Error: %d, %s" % (e.args[0], e.args[1])
            self.log = LOG()
            self.log.logger(message)
            return -1
        else:
            return self.conn

    def runQuery(self, connector, query = 'SELECT * FROM logs'):
        try:
            cursor = connector.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(query)
            self.result_set = cursor.fetchall()
        except MySQLdb.Error, e:
            message = "Error: %d, %s" % (e.args[0], e.args[1])
            self.log = LOG()
            self.log.logger(message)
            return -1
        else:
            return self.result_set

class JSONify():
    validation = {
                    'keys':['facility', 'includeFacility', 'priority', 'includePriority', 'tags', 'includeTags', 'hosts', 'includeHosts', 'message', 'includeMessages', 'searchBefore', 'searchAfter', 'page'],
                    'facility':['auth', 'authpriv', 'cron', 'daemon', 'ftp', 'kern', 'local0', 'local1', 'local2', 'local3', 'local5', 'local6', 'local7', 'lpr', 'mail', 'news', 'syslog', 'user', 'uucp'],
                    'includeFacility':[ 'include', 'exclude' ],
                    'priority':['emerg', 'alert', 'crit', 'err', 'warning', 'notice', 'info', 'debug'],
                    'includePriority':['include', 'exclude'],
                    'includeTags':['include', 'exclude'],
                    'includeHosts':['include', 'exclude'],
                    'includeMessage':['include', 'exclude'],
                    'page':['10', '25', '50', '100', '250', '500', '1000', '2500', '5000']
                 }

    def jsonToSQL(self,jsonObj):
        pLog = LOG()
        jsonDict = {}
        key = ''
        value = ''
        for jObjItem in jsonObj:
            key = jObjItem.keys()[0]
            value = jObjItem[key]
            jsonDict[key] = value

        pLog.logger("In jsonToSQL function jsonDict = %s" % str(jsonDict))

if __name__ == "__main__":
    db = DB()
    conn = db.connector('syslog')
    jObj = JSONify()
    pLog = LOG()
    response = ''

    request = cgi.FieldStorage(keep_blank_values=True)
    pLog.logger("postRawData: " + str(request))

    requestKey = request.keys()[0]
    pLog.logger("requestKey_0: " + str(requestKey))

    if requestKey == 'getForm':
        requestValue = request.getfirst(requestKey)
        if requestValue == 'hosts':
            response = json.dumps(db.runQuery(conn, 'SELECT * FROM hosts;'))
        elif requestValue == 'tags':
            response = json.dumps(db.runQuery(conn, 'SELECT * FROM tags;'))
        pLog.logger("requestKey: " + requestKey)
        pLog.logger("requestValue: " + requestValue)
    else:
        jsonreq = json.loads(requestKey)
        pLog.logger('JSON string: ' + str(jsonreq))
        jObj.jsonToSQL(jsonreq)
        response = json.dumps(db.runQuery(conn, 'SELECT id, concat(datetime) AS datetime, host, facility, priority,  tag, message FROM logs ORDER BY datetime DESC, id DESC LIMIT 25;'))

    print "Content-Type: text/plain;charset=utf-8\n\n"

    print response
