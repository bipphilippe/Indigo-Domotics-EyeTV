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
    =======
    Rev 1.0.0 : Initial version - 1st April 2015
    Rev 1.0.1 : Correction of non-critical bugs occurring only on first install - 1st April 2015
                 - cosmetic bug on Turbo.264 HD device name : corrected
                 - non-critical error on debug flag when starting the plugin for the first time : corrected
                 - non-critical error on plugin property when creating the first plugin : corrected
    Rev 1.0.2 : Bug correction - 22 april 2015
                Included bug corrections :
                 - more accurate ps command use
                 - next record timer no more generated during prepad time
                Framework update
    Rev 1.1.0 : Enhancements - 25 april 2015
                 - add a "about" menu
                 - new log management, less verbose
                 - manages the Indigo Timer time slip
                 - manages the "Enable Indigo Communication" flag
                Some bugs corrections, including :
                 - includes a 5 minutes margin to launch EyeTV before EyeTV Helper
    Rev 1.2.0 : Enhancements - 30 april 2015
                Enhancements from Framework update:
                 - applescript library error filter
                 - matching between True/False states between applescript and python
                 - uniform way of encoding strings
                 - logging
                Other enhancements:
                 - uniform way of encoding strings

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
        self.debug = False
        self.logLevel = 1

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
        core.logger(traceLog = u'startup called')
        self.timerPlugin = indigo.server.getPlugin(u'com.perceptiveautomation.indigoplugin.timersandpesters')
        self.timerPluginEnabled = self.timerPlugin.isEnabled()
        interface.init()

        core.logger(traceLog = u'end of startup')

    def shutdown(self):
        core.logger(traceLog = u'shutdown called')
        # do some cleanup here
        core.logger(traceLog = u'end of shutdown')


    ######################
    def deviceStartComm(self, dev):
        core.logger(traceLog = u' "%s" deviceStartComm called (%d - %s)' % (dev.name, dev.id, dev.deviceTypeId))
        core.logger(traceLog = u'end of "%s" deviceStartComm'  % (dev.name))

    def deviceStopComm(self, dev):
        core.logger(traceLog = u'deviceStopComm called: %s (%d - %s)' % (dev.name, dev.id, dev.deviceTypeId))
        core.logger(traceLog = u'end of "%s" deviceStopComm'  % (dev.name))


    ########################################
    # Update thread
    ########################################
    def runConcurrentThread(self):
        core.logger(traceLog = u'runConcurrentThread initiated')
        nextProgramCheck = corethread.dialogTimer(u'Next program data check',300)
        timerCheck = corethread.dialogTimer(u'Next program timer check',3600,150)
        
        try:
            while True:
                corethread.sleepWake()
                for thedevice in indigo.devices.iter('self'):
                    thevaluesDict = {}

                    ##########
                    # TurboHD App
                    ########################
                    if (thedevice.deviceTypeId ==u'bip.etv.turbohdapp') and thedevice.configured and thedevice.enabled:
                        # TurboHD states
                        (success,thevaluesDict) = interface.getProcessData(thedevice, thevaluesDict)
                        if thevaluesDict.setdefault(u'Status',u'other') != u'unavailable':
                            del thevaluesDict[u'Status']
                            (success,thevaluesDict) = interface.getTurboHDData(thedevice,thevaluesDict)
                        # update
                        theupdatesDict = core.updatestates(thedevice, thevaluesDict)
                        # special images
                        core.specialimage(thedevice, u'Status', theupdatesDict, {u'recording':indigo.kStateImageSel.SensorTripped})

                    ##########
                    # EyeTV App
                    ########################
                    elif (thedevice.deviceTypeId ==u'bip.etv.eyetvapp') and thedevice.configured and thedevice.enabled:
                        # EyeTV states
                        (success,thevaluesDict) = interface.getProcessData(thedevice, thevaluesDict)
                        if thevaluesDict.setdefault(u'Status',u'other') != u'unavailable':
                            del thevaluesDict[u'Status']
                            (success,thevaluesDict) = interface.getEyeTVData(thedevice,thevaluesDict)
                        # update
                        theupdatesDict = core.updatestates(thedevice, thevaluesDict)
                        # special images
                        core.specialimage(thedevice, u'isRecording', theupdatesDict, {u'True':indigo.kStateImageSel.SensorTripped})

                        # "next recording" timer
                        if self.timerPluginEnabled:
                            # check if an update of the values are needed
                            try:
                                # test if the timer exists
                                thetimer=indigo.devices[thedevice.pluginProps[u'TimerDevice']]
                            except:
                                # needs to create it now
                                thetimer = None
                                nextProgramCheck.doNow()
                            else:
                                if thetimer.states[u'timerStatus'] !=u'active':
                                    nextProgramCheck.doNow()
                            if (thevaluesDict.setdefault(u'Status',u'error') not in (u'unavailable',u'error')) :
                                # do not do it if error if previous steps
                                if theupdatesDict.setdefault(u'isRecording',False):
                                    nextProgramCheck.doNow()

                                if nextProgramCheck.isTime():
                                    (success, thevaluesTimerDict) = interface.getEyeTVNextProgramData(thedevice,{})
                                    if success:
                                        theupdatesTimerDict = core.updatestates(thedevice, thevaluesTimerDict)
                                        if (len(theupdatesTimerDict)>0) or (thetimer is None) or (u'PrepadTime' in theupdatesDict):
                                            success = interface.updateNextProgramTimer(thedevice, thevaluesDict, thetimer, thevaluesTimerDict)
                                    else:
                                        nextProgramCheck.doNow()
                
                            # regular check of timer (because of lack of precision)
                            if (thetimer.states[u'timerStatus'] ==u'active') and (timerCheck.isTime()):
                                interface.checkNextProgramTimer(thetimer, thedevice.states[u'StartTimestamp'], thedevice.states[u'PrepadTime'])

                # wait
                corethread.sleepNext(5) # in seconds
        except self.StopThread:
            # do any cleanup here
            core.logger(traceLog = u'end of runConcurrentThread')

    ########################################
    # Prefs UI methods (works with PluginConfig.xml):
    ######################

    # Validate the pluginConfig window after user hits OK
    # Returns False on failure, True on success
    #
    def validatePrefsConfigUi(self, valuesDict):
        core.logger(traceLog = u'validating Prefs called')

        errorMsgDict = indigo.Dict()
        err = False

        # manage debug flag
        core.debugFlags(valuesDict)

        core.logger(traceLog = u'end of validating Prefs')
        return (True, valuesDict)


    def validateDeviceConfigUi(self, valuesDict, typeId, devId):
        core.logger(traceLog = (u'validating Device Config called for: (%d - %s)') % (devId, typeId))

        core.logger(traceLog = u'end of validating Device Config')
        return (True, valuesDict)

