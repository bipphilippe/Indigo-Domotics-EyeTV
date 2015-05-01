#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################################################################################
"""
    EyeTV and TurboHD plug-in dialog interface
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
"""
####################################################################################

import indigo
from datetime import datetime
from bipIndigoFramework import core
from bipIndigoFramework import osascript
from bipIndigoFramework import shellscript


# Note the "indigo" module is automatically imported and made available inside
# our global name space by the host process.

def init():
    osascript.init()
    shellscript.init()


##########
# Any App
########################
def getProcessData(thedevice, thevaluesDict):
    """ Searches for the task in system tasklist, commons to EyetV and TurboHD

        Args:
            thedevice: current device
            thevaluesDict: dictionary of the status values so far
        Returns:
            success: True if success, False if not
            thevaluesDict updated with new data if success, equals to the input if not
    """
    pslist = shellscript.run(u"ps -awxc -opid,comm | grep '%s$'" % (thedevice.pluginProps[u'ApplicationID'][:-4]),[(0,6)],[u'ProcessID'])

    if pslist[u'ProcessID']=='':
        thevaluesDict[u'Status']=u'unavailable'

    return (True,thevaluesDict)


##########
# TurboHD App
########################
def getTurboHDData(thedevice,thevaluesDict):
    """ Gets TurboHD status
        
        Args:
            thedevice: current device
            thevaluesDict: dictionary of the status values so far
        Returns:
            success: True if success, False if not
            thevaluesDict: updated with new data if success, equals to the input if not
        """
    
    theresult = osascript.run (u'''(* Get TurboHD application data *)
        tell application "Turbo.264 HD"
            set saveTID to AppleScript's text item delimiters
            set AppleScript's text item delimiters to {"||"}
            with timeout of 2 seconds
                set toreturn to {isEncoding as string, ¬
                    isHardwarePluggedIn as string, ¬
                    lastErrorCode as string}
                if isEncoding then
                    set the end of toreturn to "recording"
                else if lastErrorCode > 0 then
                    set the end of toreturn to "error"
                else
                    set the end of toreturn to "stopped"                
                end if
                set toreturn to toreturn as text
            end timeout
            set AppleScript's text item delimiters to saveTID
        end tell
        return toreturn''',[u'isEncoding', u'isTurboHardwareIn', u'lastError', u'Status'])
    
    if theresult is not None :
        thevaluesDict.update(theresult),
        return (True,thevaluesDict)
    else:
        return (False,thevaluesDict)


##########
# EyeTV App
########################
def getEyeTVData(thedevice,thevaluesDict):
    """ Gets EyeTV status

        Args:
            thedevice: current device
            thevaluesDict: dictionary of the status values so far
        Returns:
            success: True if success, False if not
            thevaluesDict: updated with new data if success, equals to the input if not
    """

    theresult = osascript.run (u'''(* Get EyeTV application data *)
        tell application "EyeTV"
            set saveTID to AppleScript's text item delimiters
            set AppleScript's text item delimiters to {"||"}
            with timeout of 2 seconds
                set thechannel to current channel
                set toreturn to {alert menu open as text, ¬
                    (name of (channels whose channel number = thechannel)) as text, ¬
                    is Turbo Hardware Plugged In as text, ¬
                    (is_compacting or is_exporting or is_recording or is_saving_clip_as_recording or playing) as text, ¬
                    is_compacting as text, ¬
                    is_exporting as text, ¬
                    is_recording as text, ¬
                    is_saving_clip_as_recording as text, ¬
                    playing as text, ¬
                    prepad time as string, ¬
                    postpad time as string, ¬
                    (((playback volume)*100) as integer) as text, ¬
                    volume muted as text, ¬
                    server mode as text}
                if is_recording then
                    set the end of toreturn to "recording"
                else if playing then
                    set the end of toreturn to "playing"
                else if (is_compacting or is_exporting or is_saving_clip_as_recording) then
                    set the end of toreturn to "paused"
                else
                    set the end of toreturn to "stopped"
                end if
                set toreturn to toreturn as text
           end timeout
           set AppleScript's text item delimiters to saveTID
        end tell
        return toreturn''',[u'AlertMenu', u'CurrentChannel', u'isTurboHardwareIn', u'isBusy', u'isCompacting', u'isExporting', u'isRecording', u'isSavingClip', u'isPlaying', u'PrepadTime', u'PostpadTime', u'PlaybackVolume', u'isMutedVolume', u'isServerMode',u'Status'], 20)

    if theresult is not None :
        thevaluesDict.update(theresult),
        return (True,thevaluesDict)
    else:
        return (False,thevaluesDict)


def getEyeTVNextProgramData(thedevice,thevaluesDict):
    """ Get Next Program Data

        Args:
            thedevice: current EyeTV device
            thevaluesDict: dictionary of the status values so far
        Returns:
            success: True if success, False if not
            thevaluesDict: updated with new data if success, equals to the input if not
    """

     # update next program data
    theresult = osascript.run(u'''(* Find next program *)
        global theNextEyeTVProgramTime
        global theNextEyeTVProgram
        global theTime

        on run
            with timeout of 2 seconds
                tell application "EyeTV"
                    set theTime to (current date) + prepad time * 60 + 60
                    set theNextEyeTVProgram to (item 1 of (programs where (start time > theTime) and enabled = true))
                    set theNextEyeTVProgramTime to start time of theNextEyeTVProgram
                end tell
            end timeout
            loopme()
            set saveTID to AppleScript's text item delimiters
            set AppleScript's text item delimiters to {"||"}
            tell application "EyeTV"
                set thechannel to ((channel number) of theNextEyeTVProgram)
                set toreturn to {(unique ID of theNextEyeTVProgram) as string, ¬
                (title of theNextEyeTVProgram) as string, ¬
                (episode of theNextEyeTVProgram) as string, ¬
                (name of (channels whose channel number = thechannel)) as text, ¬
                (duration of theNextEyeTVProgram) as string, ¬
                (start time of theNextEyeTVProgram) as string, ¬
                my pydate(start time of theNextEyeTVProgram)} as text
            end tell
            set AppleScript's text item delimiters to saveTID
            return toreturn
        end run

        on loopme()
            with timeout of 2 seconds
                tell application "EyeTV"
                    try
                        set theNextEyeTVProgram to (item 1 of (programs where (start time > theTime) and (start time < theNextEyeTVProgramTime) and enabled = true))
                        set theNextEyeTVProgramTime to start time of theNextEyeTVProgram
                    on error
                        return
                    end try
                end tell
            end timeout
            return loopme()
        end loopme

        on pydate(mydate)
            return "" & (year of mydate) & ¬
            "-" & text -2 thru -1 of ("00" & ((month of mydate) as integer)) & ¬
            "-" & text -2 thru -1 of ("00" & (day of mydate)) & ¬
            " " & text -2 thru -1 of ("00" & (hours of mydate)) & ¬
            ":" & text -2 thru -1 of ("00" & (minutes of mydate)) & ¬
            ":" & text -2 thru -1 of ("00" & (seconds of mydate))
        end pydate''', [u'UniqueID', u'Title', u'Episode', u'ChannelName', u'Duration', u'StartTime', u'StartTimestamp'])

    if theresult is not None :
        thevaluesDict.update(theresult) ,
        return (True,thevaluesDict)
    else:
        return (False,thevaluesDict)


def updateNextProgramTimer(thedevice, thedeviceDict, thetimer, thevaluesDict):
    """ Update time regarding Next Program Data

        Args:
            thedevice: current EyeTV device
            thedeviceDict: dictionary of the status values so far
            thetimer: timer device
            thevaluesDict: timer device status values dict
        Returns:
            success: True if success, False if not
    """
    core.logger(traceLog = u'Working on timer data')

    # timer data
    theName = thevaluesDict[u'Title'] + u' - ' + thevaluesDict[u'Episode'] + u' ('+thevaluesDict[u'ChannelName'] + u')'
    theDescription = thevaluesDict[u'Title'] + u'\n' + thevaluesDict[u'Episode'] + u'\n' + thevaluesDict[u'ChannelName'] +u'\n' + thevaluesDict[u'StartTime'] + u'\n' + thevaluesDict[u'Duration'] + u' min'
    theAmount = datetime.strptime(thevaluesDict[u'StartTimestamp'], u'%Y-%m-%d %H:%M:%S') - datetime.now()
    core.logger(traceLog = u'Raw amount %s' % (theAmount))
    # wake-up 5 minutes before recording start
    theAmount = theAmount.seconds/60 + theAmount.days*24*60 - int(thedeviceDict[u'PrepadTime']) - 5
    
    if theAmount>0:
        if thetimer is None:
            # needs to create a timer device
            core.logger(traceLog = u'Creating a new timer')
            thetimer = (indigo.device.create(protocol=indigo.kProtocol.Plugin,
                     name = theName.encode('ascii', 'ignore'),
                     description= theDescription.encode('ascii', 'ignore'),
                     pluginId=u'com.perceptiveautomation.indigoplugin.timersandpesters',
                     deviceTypeId=u'timer',
                     props={u'amount':theAmount, u'amountType':u'minutes'},
                     folder=thedevice.folderId))
            indigo.activePlugin.timerPlugin.executeAction(u'startTimer', deviceId=thetimer.id)

            # update device property
            localprops = thedevice.pluginProps
            localprops.update({u'TimerDevice':thetimer.id})
            thedevice.replacePluginPropsOnServer(localprops)
            core.logger(msgLog = u'created new timer "%s" (id:%s) for %s minutes' % (theName,thetimer.id, theAmount))
        else:
            core.logger(traceLog = u'Updating the timer')
            thetimer.name = theName.encode('ascii', 'ignore')
            thetimer.description = theDescription.encode('ascii', 'ignore')
            thetimer.replaceOnServer()
            indigo.activePlugin.timerPlugin.executeAction(u'setTimerStartValue', deviceId=thetimer.id, props={u'amount':theAmount, u'amountType':u'minutes'})
            indigo.activePlugin.timerPlugin.executeAction(u'startTimer', deviceId=thetimer.id)
            core.logger(msgLog = u'updated timer "%s" (id:%s) for %s minutes' % (theName,thetimer.id, theAmount))


def checkNextProgramTimer(thetimer, StartTimestamp, PrepadTime):
    """ Check time regarding Next Program Data
        
        Args:
            StartTimestamp: time formated %Y-%m-%d %H:%M:%S
    """
    core.logger(traceLog = u'Checking timer data')
    
    # wake-up 5 minutes before recording start
    theAmount = datetime.strptime(StartTimestamp, '%Y-%m-%d %H:%M:%S') - datetime.now()
    core.logger(traceLog = u'Raw amount %s' % (theAmount))
    theAmount = theAmount.seconds/60 + theAmount.days*24*60 - int(PrepadTime) - 5
    indigo.activePlugin.timerPlugin.executeAction(u'setTimerStartValue', deviceId=thetimer.id, props={u'amount':theAmount, u'amountType':u'minutes'})
    indigo.activePlugin.timerPlugin.executeAction(u'startTimer', deviceId=thetimer.id)
    core.logger(msgLog = u'updated timer "%s" (id:%s) for %s minutes' % (thetimer.name, thetimer.id, theAmount))

