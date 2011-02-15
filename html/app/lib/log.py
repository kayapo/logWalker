__author__="kayapo"
__date__ ="$2011.02.14. 7:47:29$"

import syslog

class log():
    """
    Send log messages to syslog
    syslogtag = str(), facility = int(), priority = int(), message = str()
    are input parameters
    """
    syslogtag = str()
    message = str()
    facilitys  = [syslog.LOG_USER, syslog.LOG_CRON, syslog.LOG_LOCAL0, syslog.LOG_LOCAL1, syslog.LOG_LOCAL2, syslog.LOG_LOCAL3, syslog.LOG_LOCAL4, syslog.LOG_LOCAL5, syslog.LOG_LOCAL6, syslog.LOG_LOCAL7]
    prioritys = [syslog.LOG_DEBUG, syslog.LOG_INFO, syslog.LOG_NOTICE, syslog.LOG_WARNING, syslog.LOG_ERR, syslog.LOG_CRIT, syslog.LOG_ALERT, syslog.LOG_EMERG]
    facility = facilitys[0]
    priority = prioritys[0]

    def __init__(self, facility = 0, priority = 0, syslogtag = "python.logWalker"):
        """Initiate syslog parameters"""

        self.priority  = self.prioritys[priority]
        self.facility  = self.facilitys[facility]
        self.syslogtag = syslogtag

    def __del__(self):
        """destroctor"""
        return

    def logger(self, message):
        """Send log message to the syslog with preset parameters"""

        syslog.openlog(self.syslogtag, (syslog.LOG_PID + syslog.LOG_NOWAIT), self.facility)
        syslog.syslog(self.priority, message)
        syslog.closelog()
