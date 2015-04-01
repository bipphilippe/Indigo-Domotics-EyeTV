#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################################################################################
""" Basic Framework helpers for indigo plugins concurrentThread
    
    By Bernard Philippe (bip.philippe) (C) 2015

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.#


    History
    Rev 1.0.0 :   initial version
"""
####################################################################################

import indigo
import core
import time
from threading import Timer

########################################
def sleepNext(thetime):
    """ Calculate sleep time according main dialog pace
        
        Args:
            thetime: time in seconds between two dialog calls
    """

    nextdelay = thetime - (time.time() - indigo.activePlugin.wakeup)

    nextdelay = round(nextdelay,2)
    if nextdelay < 1:
        nextdelay = 0.5

    core.logger(traceLog = u"going to sleep for %s seconds" % (nextdelay))
    indigo.activePlugin.sleep(nextdelay)


def sleepWake():
    """ Take the time before one ConcurrentThread run
    """

    indigo.activePlugin.wakeup = time.time()


########################################
class dialogTimer(object):
    """ Timer to be used in runConcurrentThread for dialogs that needs to be made less often that the runConcurrentThread pace
    """
    def __init__(self, timername, interval):
        """ Constructor

            Args:
                timername : name of the timer (for logging use)
                interval: interval in seconds
            Returns:
                dialogTimer class instance
        """
        self._timer     = None
        self.timername = timername
        self.interval   = interval
        self.timeEllapsed = True
        core.logger(traceLog = u"initiating dialog timer \"%s\" on a %s seconds pace" % (self.timername, interval))
        self._run()

    def __del__(self):
        core.logger(traceLog = u"deleting dialog timer \"%s\"" % (self.timername))
        self._timer.cancel()
    
    def _run(self):
        core.logger(traceLog = u"time ellapsed for dialog timer \"%s\"" % (self.timername))
        self.timeEllapsed = True
        self._timer = Timer(self.interval, self._run)
        self._timer.start()

    def doNow(self):
        """ Stop the current timing and set isTime to true
        """
        core.logger(traceLog = u"forced time ellapsed for dialog timer \"%s\"" % (self.timername))
        self._timer.cancel()
        self._run()

    def isTime(self):
        """ True if the timing is ellapsed
            
            Note : returns true When the class instance is created
        """
        if self.timeEllapsed:
            self.timeEllapsed = False
            return True
        else:
            return False
