#!/usr/bin/env python

__author__="kayapo"
__date__ ="$2011.02.04. 18:18:33$"
__TODO__ = "Minden fuggvenyt es osztalyt kommentezni"

import sys
import MySQLdb
import syslog
import json
import cgi
import re
import time

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
    dateValidation = [ 'before', 'after' ]
    textValidation = [ 'message' ]

    whereClausePatch = { 'include':'IN', 'exclude': 'NOT IN' }
    whereClauseMessagePatch = { 'include':'MATCH', 'exclude': 'NOT MATCH' }

    def __init__(self):
        db = DB()
        conn = db.connector("syslog")
        pLog = LOG()
        
        tags = db.runQuery(conn, "SELECT tag FROM tags;")
        if Config.debug == 1: pLog.logger("Tags in JSONify %s" % str(tags))
        realTags = []
        for tag in tags:
            realTags.append(tag['tag'])

        self.validation["tags"] = realTags
        
        hosts = db.runQuery(conn, "SELECT host FROM hosts;")
        if Config.debug == 1: pLog.logger("Hosts in JSONify %s" % str(hosts))
        realHosts = []
        for host in hosts:
            realHosts.append(host['host'])

        self.validation["hosts"] = realHosts

        if Config.debug == 1: pLog.logger("JSONify.validation = %s" % self.validation)


    def jsonToSQL(self,jsonObj):
        pLog = LOG()
        jsonDict = dict()

        SELECT = [ "id", "concat(datetime) AS datetime", "host", "facility", "priority",  "tag", "message" ]
        WHERE = list()
        ORDER = [ "id DESC" ]

        for jObjItem in jsonObj:
            key = str()
            value = str()
            keyUnreliable = jObjItem.keys()[0]
            key = list(set(self.validation["keys"]).intersection(set([keyUnreliable])))[0]
            valueUnreliable = jObjItem[key]
            if key in self.validation.keys():
                if type(valueUnreliable).__name__ == 'list':
                    value = list(set(self.validation[key]).intersection(set(valueUnreliable)))
                    if Config.debug == 1: pLog.logger("Validated list type input: %s" % str(value))
                else:
                    value = list(set(self.validation[key]).intersection(set([valueUnreliable])))[0]
                    if Config.debug == 1: pLog.logger("Validated not list type input: %s" % str(value))
            elif key in self.dateValidation:
                if valueUnreliable != '' and self.dateValidation.__contains__(key):
                    if re.search('^2[0-9]{3}-(0[1-9]|1[012])-([012][0-9]|3[01]) ([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$', valueUnreliable):
                        value = valueUnreliable
                    else:
                        if key == 'after':
                            value = '1970:01:01 00:00:00'
                        elif key == 'before':
                            value = time.strftime('%Y-%m-%d %H:%M:%S')
                    if Config.debug == 1: pLog.logger("Validated date type input: %s" % str(value))
            else:
                if Config.debug == 1: pLog.logger("Need other validation: %s" % str(value))
                # A message mezo validalasa hianyzik meg
                value = valueUnreliable
            
            if Config.debug == 1: pLog.logger("jsonDict[%s] = %s" % (key, value))
            jsonDict[key] = value

        if Config.debug == 1: pLog.logger("In jsonToSQL function jsonDict = %s" % str(jsonDict))

        if len(jsonDict['facility']) > 0:
            WHERE.append( "`facility` " + self.whereClausePatch[jsonDict['includeFacility']] + "('" + "', '".join(jsonDict['facility']) + "')" )

        if len(jsonDict['priority']) > 0:
            WHERE.append( "`priority` " + self.whereClausePatch[jsonDict['includePriority']] + "('" + "', '".join(jsonDict['priority']) + "')" )

        if len(jsonDict['hosts']) > 0:
            WHERE.append( "`host` " + self.whereClausePatch[jsonDict['includeHosts']] + "('" + "', '".join(jsonDict['hosts']) + "')" )

        if len(jsonDict['tags']) > 0:
            WHERE.append( "`tag` " + self.whereClausePatch[jsonDict['includeTags']] + "('" + "', '".join(jsonDict['tags']) + "')" )

        if jsonDict['message'] != '':
            WHERE.append( self.whereClauseMessagePatch[jsonDict['includeMessage']] + "(`message`) AGAINST('" + jsonDict['message'] + "' IN BOOLEAN MODE)"  )
            SELECT.append( "MATCH(`message`) AGAINST('" + jsonDict['message'] + "' IN BOOLEAN MODE) AS score" )
            ORDER = [ "score DESC" ] + ORDER

        if jsonDict["before"] != '' and ( "searchBefore" in jsonDict.keys() ):
            WHERE.append( "`datetime` < '" + jsonDict['before'] + "'" )

        if jsonDict["after"] != '' and ( "searchAfter" in jsonDict.keys() ):
            WHERE.append( " `datetime` > '" + jsonDict["after"] + "'" )

        LIMIT = " LIMIT " + jsonDict['page']

        sqlQuerry = "SELECT " + ( ", ".join(SELECT) ) + " FROM logs"

        if len(WHERE) > 0:
            sqlQuerry += " WHERE " + " AND ".join(WHERE)

        if len(ORDER) > 0:
            sqlQuerry += " ORDER BY " + ", ".join(ORDER)

        sqlQuerry += LIMIT + ";"

        if Config.debug == 1: pLog.logger( "The querry: " + sqlQuerry )

        return sqlQuerry

if __name__ == "__main__":
    db = DB()
    conn = db.connector('syslog')
    jObj = JSONify()
    pLog = LOG()
    response = ''

    request = cgi.FieldStorage(keep_blank_values=True)
    if Config.debug == 1: pLog.logger("postRawData: " + str(request))

    requestKey = request.keys()[0]
    requestValue = str(request[request.keys()[0]].value)
    if Config.debug == 1: pLog.logger("requestKey_0: " + str(requestKey))

    if requestKey == 'getForm':
        if requestValue == 'hosts':
            response = json.dumps(db.runQuery(conn, 'SELECT * FROM hosts;'))
        elif requestValue == 'tags':
            response = json.dumps(db.runQuery(conn, 'SELECT * FROM tags;'))
        if Config.debug == 1: pLog.logger("requestKey: " + requestKey)
        if Config.debug == 1: pLog.logger("requestValue: " + requestValue)
    elif requestKey == 'data':
        jsonreq = json.loads(requestValue)
        if Config.debug == 1: pLog.logger('JSON string: ' + str(jsonreq))
        sql = jObj.jsonToSQL(jsonreq)
        response = json.dumps(db.runQuery(conn, sql))

    print "Content-Type: text/plain;charset=utf-8\n\n"

    print response
