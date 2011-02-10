#!/usr/bin/env python

__author__="kayapo"
__date__ ="$2011.02.04. 18:18:33$"
__TODO__ = "Minden fuggvenyt es osztalyt kommentezni"

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
                    'keys':['facility', 'includeFacility', 'priority', 'includePriority', 'tags', 'includeTags', 'hosts', 'includeHosts', 'message', 'includeMessage', 'searchBefore', 'searchAfter', 'page', 'before', 'after'],
                    'facility':['auth', 'authpriv', 'cron', 'daemon', 'ftp', 'kern', 'local0', 'local1', 'local2', 'local3', 'local5', 'local6', 'local7', 'lpr', 'mail', 'news', 'syslog', 'user', 'uucp'],
                    'includeFacility':[ 'include', 'exclude' ],
                    'priority':['emerg', 'alert', 'crit', 'err', 'warning', 'notice', 'info', 'debug'],
                    'includePriority':['include', 'exclude'],
                    'includeTags':['include', 'exclude'],
                    'includeHosts':['include', 'exclude'],
                    'includeMessage':['include', 'exclude'],
                    'page':['10', '25', '50', '100', '250', '500', '1000', '2500', '5000'],
                    'searchAfter':['on'],
                    'searchBefore':['on']
                 }

    def __init__(self):
        db = DB()
        conn = db.connector("syslog")
        pLog = LOG()
        
        tags = db.runQuery(conn, "SELECT tag FROM tags;")
        pLog.logger("Tags in JSONify %s" % str(tags))
        realTags = []
        for tag in tags:
            realTags.append(tag['tag'])

        self.validation["tags"] = realTags
        
        hosts = db.runQuery(conn, "SELECT host FROM hosts;")
        pLog.logger("Hosts in JSONify %s" % str(hosts))
        realHosts = []
        for host in hosts:
            realHosts.append(host['host'])

        self.validation["hosts"] = realHosts

        pLog.logger("JSONify.validation = %s" % self.validation)


    def jsonToSQL(self,jsonObj):
        pLog = LOG()
        jsonDict = {}
        key = ''
        value = ''
        for jObjItem in jsonObj:
            keyUnreliable = jObjItem.keys()[0]
            key = list(set(self.validation["keys"]).intersection(set([keyUnreliable])))[0]
            valueUnreliagle = jObjItem[key]
            if key in self.validation.keys():
                if type(valueUnreliagle).__name__ == 'list':
                    value = list(set(self.validation[key]).intersection(set(valueUnreliagle)))
                    pLog.logger("Validated list type input: %s" % str(value))
                else:
                    value = list(set(self.validation[key]).intersection(set([valueUnreliagle])))[0]
                    pLog.logger("Validated not list type input: %s" % str(value))
            else:
                value = jObjItem[key]
                pLog.logger("Need other validation: %s" % str(value))
            
            pLog.logger("jsonDict[%s] = %s" % (key, value))
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
    requestValue = str(request[request.keys()[0]].value)
    pLog.logger("requestKey_0: " + str(requestKey))

    if requestKey == 'getForm':
        if requestValue == 'hosts':
            response = json.dumps(db.runQuery(conn, 'SELECT * FROM hosts;'))
        elif requestValue == 'tags':
            response = json.dumps(db.runQuery(conn, 'SELECT * FROM tags;'))
        pLog.logger("requestKey: " + requestKey)
        pLog.logger("requestValue: " + requestValue)
    elif requestKey == 'data':
        jsonreq = json.loads(requestValue)
        pLog.logger('JSON string: ' + str(jsonreq))
        jObj.jsonToSQL(jsonreq)
        response = json.dumps(db.runQuery(conn, 'SELECT id, concat(datetime) AS datetime, host, facility, priority,  tag, message FROM logs ORDER BY datetime DESC, id DESC LIMIT 25;'))

    print "Content-Type: text/plain;charset=utf-8\n\n"

    print response
