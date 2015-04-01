#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################################################################################
"""
    EyeTV plug-in
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

import sys
from bipIndigoFramework import core
from bipIndigoFramework import corethread
import interface


# Note the "indigo" module is automatically imported and made available inside
# our global name space by the host process.

################################################################################
class Plugin(indigo.PluginBase):
    ########################################
    def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
        indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)

    def __del__(self):
        indigo.PluginBase.__del__(self)

    ########################################
    # Indigo plugin functions
    #
    #
    ########################################
    def startup(self):
        # first read debug flags - before any logging
        core.debugFlags(self.pluginPrefs)
        # startup call
        core.logger(traceLog = u"startup called")
        self.timerPlugin = indigo.server.getPlugin("com.perceptiveautomation.indigoplugin.timersandpesters")
        self.timerPluginEnabled = self.timerPlugin.isEnabled()
        interface.init()

        core.logger(traceLog = u"end of startup")

    def shutdown(self):
        core.logger(traceLog = u"shutdown called")
        # do some cleanup here
        core.logger(traceLog = u"end of shutdown")


    ######################
    def deviceStartComm(self, dev):
        core.logger(traceLog = u"deviceStartComm called for: %s (%d - %s)" % (dev.name, dev.id, dev.deviceTypeId))
        core.logger(traceLog = u"end of deviceStartComm")

    def deviceStopComm(self, dev):
        core.logger(traceLog = u"deviceStopComm called: %s (%d - %s)" % (dev.name, dev.id, dev.deviceTypeId))
        core.logger(traceLog = u"end of deviceStopComm")

    ######################
    #def triggerStartProcessing(self, trigger):
    #    core.logger(traceLog = u"triggerStartProcessing called for: %s (%d)" % (trigger.name, trigger.id))
    #
    #    core.logger(traceLog = u"end of triggerStartProcessing")

    # def triggerStopProcessing(self, trigger):
    #    core.logger(traceLog = u"triggerStopProcessing called for: %s (%d)" % (trigger.name, trigger.id))
    #
    #    core.logger(traceLog = u"end of triggerStopProcessing")


    ########################################
    # Update thread
    ########################################
    def runConcurrentThread(self):
        core.logger(traceLog = u"runConcurrentThread initiated")
        nextProgramCheck = corethread.dialogTimer("Next program data check",300)
        try:
            while True:
                corethread.sleepWake()
                for thedevice in indigo.devices.iter("self"):
                    thevaluesDict = {}

                    ##########
                    # TurboHD App
                    ########################
                    if (thedevice.deviceTypeId =="bip.etv.turbohdapp"):
                        # TurboHD states
                        (success,thevaluesDict) = interface.getProcessData(thedevice, thevaluesDict)
                        if thevaluesDict.setdefault("Status","other") != "unavailable":
                            del thevaluesDict["Status"]
                            (success,thevaluesDict) = interface.getTurboHDData(thedevice,thevaluesDict)
                        # update
                        theupdatesDict = core.updatestates(thedevice, thevaluesDict)
                        # special images
                        core.specialimage(thedevice, "Status", theupdatesDict, {"recording":indigo.kStateImageSel.SensorTripped})

                    ##########
                    # EyeTV App
                    ########################
                    elif (thedevice.deviceTypeId =="bip.etv.eyetvapp"):
                        # EyeTV states
                        (success,thevaluesDict) = interface.getProcessData(thedevice, thevaluesDict)
                        if thevaluesDict.setdefault("Status","other") != "unavailable":
                            del thevaluesDict["Status"]
                            (success,thevaluesDict) = interface.getEyeTVData(thedevice,thevaluesDict)
                        # update
                        theupdatesDict = core.updatestates(thedevice, thevaluesDict)
                        # special images
                        core.specialimage(thedevice, "isRecording", theupdatesDict, {"true":indigo.kStateImageSel.SensorTripped})

                        # "next recording" timer
                        if self.timerPluginEnabled and (thevaluesDict.setdefault("Status","error") not in ("unavailable","error")) :
                            # do not do it if error if previous steps
                            try:
                                # test if the timer exists
                                thetimer=indigo.devices[thedevice.pluginProps["TimerDevice"]]
                            except:
                                # needs to create it now
                                thetimer = None
                                nextProgramCheck.doNow()
                            else:
                                if thetimer.states["timerStatus"] != "active":
                                    nextProgramCheck.doNow()

                            if theupdatesDict.setdefault("isRecording",False):
                                nextProgramCheck.doNow()

                            if nextProgramCheck.isTime():
                                (success, thevaluesTimerDict) = interface.getEyeTVNextProgramData(thedevice,{})
                                if success:
                                    theupdatesTimerDict = core.updatestates(thedevice, thevaluesTimerDict)
                                    if (len(theupdatesTimerDict)>0) or (thetimer is None) or ("PrepadTime" in theupdatesDict) or (thetimer.states["timerStatus"] != "active"):
                                        success = interface.updateNextProgramTimer(thedevice, thevaluesDict, thetimer, thevaluesTimerDict)
                                else:
                                    nextProgramCheck.doNow()

                # wait
                corethread.sleepNext(5) # in seconds
        except self.StopThread:
            # do any cleanup here
            core.logger(traceLog = u"end of runConcurrentThread")

    ########################################
    # Prefs UI methods (works with PluginConfig.xml):
    ######################

    # Validate the pluginConfig window after user hits OK
    # Returns False on failure, True on success
    #
    def validatePrefsConfigUi(self, valuesDict):
        core.logger(traceLog = u"validating Prefs called")

        errorMsgDict = indigo.Dict()
        err = False

        # manage debug flag
        core.debugFlags(valuesDict)

        core.logger(traceLog = u"end of validating Prefs")
        return (True, valuesDict)


    def validateDeviceConfigUi(self, valuesDict, typeId, devId):
        core.logger(traceLog = (u"validating Device Config called for:    (%d - %s)") % ( devId, typeId))

        core.logger(traceLog = u"end of validating Device Config")
        return (True, valuesDict)

