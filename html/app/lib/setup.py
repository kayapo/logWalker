# -*- coding: utf-8 -*-
__author__="kayapo"
__date__ ="$2011.02.17. 13:02:43$"

import re
import time
import os
import sys


class setup():
    """A variety of executive setting functions"""
    def __init__(self):
        """Initiate and include some class"""
        dir = os.path.dirname(__file__)
        includedir = os.path.join(dir, "../")
        sys.path.append(includedir)

        from lib.log import *
        from conf.Config import *

        self.Conf = Config()
        self.Log = log()

    def __del__(self):
        """Destructor"""
        self.Conf = None
        self.log = None
        return

    def identifiString(self, string = str()):
        """Identify a database name string"""
        formated = str()
        if not re.search(r"%[xXc]", string, re.U):
            formated = time.strftime(string)

        return formated

    def getMySQLhost(self):
        """Return MySQL host"""
        return self.Conf.MySQLconnector["host"]

    def getMySQLuser(self):
        """Return MySQL user name"""
        return self.Conf.MySQLconnector["user"]

    def getMySQLpassword(self):
        """Return MySQL users password"""
        return self.Conf.MySQLconnector["password"]

    def getMySQLdatabase(self):
        """Return the reformated log db string"""
        dbName = self.identifiString(self.Conf.MySQLconnector["database"])
        return dbName

    def getMySQLtable(self):
        """Return the reformated log table name"""
        tblName = self.identifiString(self.Conf.MySQLconnector["table"])
        return tblName

    def getLogLevel(self):
        """Return the loging level"""
        return self.Conf.loglevel