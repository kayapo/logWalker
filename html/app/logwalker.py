#!/usr/bin/env python

__author__="kayapo"
__date__ ="$2011.02.14. 12:22:35$"


import cgi

import json
import time
import re

from lib.log import log
from lib.db import db
from conf.Config import Config
from lib.JSONify import JSONify

#if Config.debug == 1:
#    import cgitb
#    cgitb.enable()

def getTags():
    tags = list()
    dbObj = db(Config.MySQLconnector["host"], Config.MySQLconnector["user"], Config.MySQLconnector["password"], Config.MySQLconnector["database"])
    dbConn = dbObj.connector()

    unreliableTags = dbObj.runQuery(dbConn, "SELECT * FROM tags;")
    for tag in unreliableTags:
        tags.append( {"tag":cgi.escape(tag["tag"], 1)} )
    if Config.debug == 1:
        L = log(0, 7, "logwalker.getTags")
        L.logger(str(tags))

    return tags

def getHosts():
    hosts = list()
    dbObj = db(Config.MySQLconnector["host"], Config.MySQLconnector["user"], Config.MySQLconnector["password"], Config.MySQLconnector["database"])
    dbConn = dbObj.connector()
    
    unreliableHosts = dbObj.runQuery(dbConn, "SELECT * FROM hosts;")
    for host in unreliableHosts:
        hosts.append( {"host":cgi.escape(host["host"], 1)} )
    if Config.debug == 1:
        L = log(0, 7, "logwalker.getHosts")
        L.logger(str(hosts))

    return hosts

def getRequestValidity(mode):
    """Get list for the validity object"""

    dbObj = db(Config.MySQLconnector["host"], Config.MySQLconnector["user"], Config.MySQLconnector["password"], Config.MySQLconnector["database"])
    dbConn = dbObj.connector()
    ret = list()

    if mode == 'hosts':
        query = 'SELECT * FROM hosts'
        tag = 'host'
    elif mode == 'tags':
        query = 'SELECT * FROM tags'
        tag = 'tag'

    retObj = dbObj.runQuery(dbConn, query)
    for retElement in retObj:
        ret.append(retElement[tag])

    return ret

def requestReformat(request):
    """Reformat request list to another format"""

    L = log(0, 7, "logwalker.requestReformat")
    reformated = {}

    if type(request).__name__ == 'list':
        for element in request:
            key = element.keys()[0]
            value = element[key]
            if Config.debug == 1: L.logger('%s => %s' % (key, str(value)))

            reformated[key] = value

    return reformated

if __name__ == "__main__":
    L = log(0, 7, "logwalker.main")
    J = JSONify()
    D = db(Config.MySQLconnector["host"], Config.MySQLconnector["user"], Config.MySQLconnector["password"], Config.MySQLconnector["database"])

    response = "Cache-Control: no-cache\nPragma: no-cache\nExpires: 0\nContent-Type: text/plain;charset=utf-8\n\n"
    request = cgi.FieldStorage(keep_blank_values=True)
    if Config.debug == 1: L.logger("postRawData: " + str(request))

    try:
        requestKey = request.keys()[0]
        requestValue = str(request[request.keys()[0]].value)
        requestValue = re.sub("[\n\r]", " ", requestValue)
    except IndexError, e:
        L.logger("Error: %s" % e.args[0])
        requestKey = ''

    if requestKey == 'getForm':
        if requestValue == 'hosts':
            response += json.dumps(getHosts())
        elif requestValue == 'tags':
            response += json.dumps(getTags())
        if Config.debug == 1:
            L.logger("requestKey = " + requestKey)
            L.logger("requestValue = " + requestValue)

    elif requestKey == 'data':


        jsonreq = json.loads(requestValue)
        if Config.debug == 1: L.logger('JSON string = ' + str(jsonreq))

        reformatedRequest = requestReformat(jsonreq)

        J.selectionValidation["tags"] = getRequestValidity("tags")
        J.selectionValidation["hosts"] = getRequestValidity("hosts")
        
        validatedRequest = J.validityCheck(reformatedRequest)

        if Config.debug == 1: L.logger("sql Query = " + J.objectToSQL(reformatedRequest))
        sql = J.objectToSQL(reformatedRequest)
        dbConn = D.connector()

        response += json.dumps(D.runQuery(dbConn, sql))

    elif requestKey == '':
        response = "Status: 301 Permanently moved\nLocation: /index.html\n"
    else:
        response += '[{"facility": "user", "datetime": "%s", "priority": "err", "host": "localhost", "tag": "logwalker", "message": "Request error!!!", "id": 1}]' % (time.strftime('%Y-%m-%d %H:%M:%S'))


    print response

