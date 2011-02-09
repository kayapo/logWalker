#!/usr/bin/env python

import cgi
import json

print "Content-type: text/plain\n\n"
postData = cgi.FieldStorage(keep_blank_values=True)

print json.loads(postData)