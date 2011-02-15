#!/usr/bin/env python

#from html.app.lib.db import db
import sys
sys.path.append('../html/app/conf/')
sys.path.append('../html/app/lib/')

from Config import Config
from db import db

def main():
    dbObj = db(Config.MySQLconnector["host"], Config.MySQLconnector["user"], Config.MySQLconnector["password"], Config.MySQLconnector["database"])
    dbConn = dbObj.connector()

    logTableTags = dbObj.runQuery(dbConn, "SELECT tag FROM logs GROUP BY tag;")
    tagTableTags = dbObj.runQuery(dbConn, "SELECT tag FROM tags;")
    logTableHosts = dbObj.runQuery(dbConn, "SELECT host FROM logs GROUP BY host;")
    hostTableHosts = dbObj.runQuery(dbConn, "SELECT host FROM hosts;")

    tagTags = list()
    hostHosts = list()

    for T in tagTableTags:
        tagTags.append(T["tag"])

    for H in hostTableHosts:
        hostHosts.append(H["host"])

    for T in logTableTags:
        if T["tag"] not in tagTags:
            query = "INSERT INTO tags(`tag`) VALUE('%s');" % T["tag"]
            dbObj.runQuery(dbConn, query)

    for H in logTableHosts:
        if H["host"] not in hostHosts:
            query = "INSERT INTO hosts(`host`) VALUE('%s');" % H["host"]
            dbObj.runQuery(dbConn, query)

    return

if __name__ == "__main__":
    main()
