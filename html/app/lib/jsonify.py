__author__="kayapo"
__date__ ="$2011.02.14. 13:02:43$"

import re
import time

import sys
sys.path.append("./")
sys.path.append("../../conf/")

from db import DB
from config import Config

class JSONify():
    """JSON object conrezation"""

    validKeys = ['facility', 'includeFacility', 'priority', 'includePriority', 'tags', 'includeTags', 'hosts', 'includeHosts', 'message', 'includeMessage', 'searchBefore', 'searchAfter', 'page', 'before', 'after']
    selectionValidation = {
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

    def __init__(self):
        dbObj = DB(Config.MySQLconnector["host"], Config.MySQLconnector["user"], Config.MySQLconnector["password"], "syslog")
        dbConn = dbObj.connector()

        tags = dbObj.runQuerry(dbConn, "SELECT * FROM tags;")
        realTags = []
        for tag in tags:
            realTags.append(tag['tag'])

        self.selectionValidation["tags"] = realTags

        hosts = dbObj.runQuerry(dbConn, "SELECT * FROM hosts;")
        realHosts = []
        for host in hosts:
            realHosts.append(host['host'])

        self.selectionValidation["hosts"] = realHosts

    def __del__(self):
        """destructor"""
        
        return

    def objectToSQL(self, jsonDict):
        """
        Convert json input to SQL querry
        jsonDict = dict()
        are input parameter
        """

        SELECT = [ "id", "concat(datetime) AS datetime", "host", "facility", "priority",  "tag", "message" ]
        WHERE = list()
        ORDER = [ "id DESC" ]

        whereClausePatch = { 'include':'IN', 'exclude': 'NOT IN' }
        whereClauseMessagePatch = { 'include':'MATCH', 'exclude': 'NOT MATCH' }

        if len(jsonDict['facility']) > 0:
            WHERE.append( "`facility` " + whereClausePatch[jsonDict['includeFacility']] + "('" + "', '".join(jsonDict['facility']) + "')" )

        if len(jsonDict['priority']) > 0:
            WHERE.append( "`priority` " + whereClausePatch[jsonDict['includePriority']] + "('" + "', '".join(jsonDict['priority']) + "')" )

        if len(jsonDict['hosts']) > 0:
            WHERE.append( "`host` " + whereClausePatch[jsonDict['includeHosts']] + "('" + "', '".join(jsonDict['hosts']) + "')" )

        if len(jsonDict['tags']) > 0:
            WHERE.append( "`tag` " + whereClausePatch[jsonDict['includeTags']] + "('" + "', '".join(jsonDict['tags']) + "')" )

        if jsonDict['message'] != '':
            WHERE.append( whereClauseMessagePatch[jsonDict['includeMessage']] + "(`message`) AGAINST('" + jsonDict['message'] + "' IN BOOLEAN MODE)"  )
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

        return sqlQuerry

    def validityCheck(self, unreliableJSONDict):
        """
        Validate json object
        unreliableJSONDict = dict()
        are input parameter
        """
        validatedJSONDict = dict()

        for unreliableKey in unreliableJSONDict.keys():
            key = str()
            if unreliableKey in self.validKeys:
                key = unreliableKey
                valueUnreliable = unreliableJSONDict[key]
                if key in self.selectionValidation.keys():
                    if type(valueUnreliable).__name__ == 'list':
                        value = list(set(self.selectionValidation[key]).intersection(set(valueUnreliable)))
                    else:
                        value = list(set(self.selectionValidation[key]).intersection(set([valueUnreliable])))
                elif key in self.dateValidation:
                    if valueUnreliable != '' and self.dateValidation.__contains__(key):
                        if re.search('^2[0-9]{3}-(0[1-9]|1[012])-([012][0-9]|3[01]) ([01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]$', valueUnreliable):
                            value = valueUnreliable
                        else:
                            if key == 'after':
                                value = '1970:01:01 00:00:00'
                            elif key == 'before':
                                value = time.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    # text message validation
                    value = valueUnreliable

                validatedJSONDict[key] = value

        return validatedJSONDict

