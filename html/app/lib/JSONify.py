# -*- coding: utf-8 -*-
__author__="kayapo"
__date__ ="$2011.02.14. 13:02:43$"

import re
import time

import sys
sys.path.append("./")

from log import *

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
        sqlQuery = "SELECT " + ( ", ".join(SELECT) ) + " FROM logs"

        if len(WHERE) > 0:
            sqlQuery += " WHERE " + " AND ".join(WHERE)

        if len(ORDER) > 0:
            sqlQuery += " ORDER BY " + ", ".join(ORDER)

        sqlQuery += LIMIT + ";"

        return sqlQuery

    def validityCheck(self, unreliableJSONDict):
        """
        Validate json object
        unreliableJSONDict = dict()
        are input parameter
        """
        validatedJSONDict = dict()
        L = log(0,7,"logwalker.lib.JSONify.validityCheck")

        for unreliableKey in unreliableJSONDict.keys():
            key = str()
            value = type(unreliableJSONDict[unreliableKey])
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
                    # Wow, it is unbelievable:
                    valueUnreliable = re.sub(re.escape("\\"), "\\\\", r"%s" % valueUnreliable)
                    value = re.sub("""([/|&{}#@^~'";-])""", lambda m: "\%s" % m.group(1), r"%s" % valueUnreliable)
                    L.logger('value = ' + value)
                    
                validatedJSONDict[key] = value

        return validatedJSONDict

    def messageClean(self,msg):
        """Cleanup <script></script> tags from message"""
        retMsg = ()
        for mLine in msg:
            mLine["message"] = re.sub("<(script[^<>]*/*)>", lambda m: "&lt;%s&gt;" % m.group(1), r"%s" % mLine["message"])
            mLine["message"] = re.sub("<(link[^<>]*/*)>", lambda m: "&lt;%s&gt;" % m.group(1), r"%s" % mLine["message"])
            mLine["message"] = re.sub("</script>", "&lt;/script&gt;", r"%s" % mLine["message"])
            mLine["message"] = re.sub("</link>", "&lt;/script&gt;", r"%s" % mLine["message"])
            mLine["message"] = re.sub("<%=(.*)%>", lambda m: r"&nbsp;&nbsp;&nbsp;<a href='%s' target='_blank'><img src='imgs/view.png' width='16' height='14' border='0' alt='view message' /></a>" % m.group(1), r"%s" % mLine["message"])

            retMsg += (mLine,)

        return retMsg