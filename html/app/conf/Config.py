# -*- coding: utf-8 -*-
class Config():
    ##	%a	Locale’s abbreviated weekday name.
    ##	%A	Locale’s full weekday name.
    ##	%b	Locale’s abbreviated month name.
    ##	%B	Locale’s full month name.
    ##	%d	Day of the month as a decimal number [01,31].
    ##	%H	Hour (24-hour clock) as a decimal number [00,23].
    ##	%I	Hour (12-hour clock) as a decimal number [01,12].
    ##	%j	Day of the year as a decimal number [001,366].
    ##	%m	Month as a decimal number [01,12].
    ##	%M	Minute as a decimal number [00,59].
    ##	%p	Locale’s equivalent of either AM or PM.
    ##	%S	Second as a decimal number [00,61].
    ##	%U	Week number of the year (Sunday as the first day of the week) as
    ##          a decimal number [00,53]. All days in a new year preceding the
    ##          first Sunday are considered to be in week 0.
    ##	%w	Weekday as a decimal number [0(Sunday),6].
    ##	%W	Week number of the year (Monday as the first day of the week) as
    ##          a decimal number [00,53]. All days in a new year preceding the
    ##          first Monday are considered to be in week 0.
    ##	%y	Year without century as a decimal number [00,99].
    ##	%Y	Year with century as a decimal number.
    ##	%Z	Time zone name (no characters if no time zone exists).
    ##	%%	A literal '%' character.
    MySQLconnector = {
                      'host':'localhost',
                      'user':'user',
                      'password':'userpassword',
                      'database':'syslog',
                      'table':'logs'
                     }
    loglevel = 0
