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


    History
    Rev 1.0.0 :   initial version
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
    osascript.initErrorHandling()

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
    pslist = shellscript.run(u"ps -awx | grep '" + thedevice.pluginProps['ApplicationID'] + "/Contents/MacOS/" + thedevice.pluginProps['ApplicationID'][:-4]+ "$'",[(0,6)],['ProcessID'])

    if pslist['ProcessID']=='':
        thevaluesDict["Status"]="unavailable"

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
        return toreturn''',["isEncoding", "isTurboHardwareIn", "lastError", "Status"])
    
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
        return toreturn''',["AlertMenu", "CurrentChannel", "isTurboHardwareIn", "isBusy", "isCompacting", "isExporting", "isRecording", "isSavingClip", "isPlaying", "PrepadTime", "PostpadTime", "PlaybackVolume", "isMutedVolume", "isServerMode","Status"], 20)

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

        on run
            with timeout of 2 seconds
                tell application "EyeTV"
                    set theNextEyeTVProgram to (item 1 of (programs where (start time > (current date)) and enabled = true))
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
                (start time of theNextEyeTVProgram) as string, my pydate(start time of theNextEyeTVProgram)} as text
            end tell
            set AppleScript's text item delimiters to saveTID
            return toreturn
        end run

        on loopme()
            with timeout of 2 seconds
                tell application "EyeTV"
                    try
                        set theNextEyeTVProgram to (item 1 of (programs where (start time > (current date)) and (start time < theNextEyeTVProgramTime) and enabled = true))
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
        end pydate''', ["UniqueID", "Title", "Episode", "ChannelName", "Duration", "StartTime", "StartTimestamp"])

    if theresult is not None :
        thevaluesDict.update(theresult) ,
        return (True,thevaluesDict)
    else:
        return (False,thevaluesDict)

def updateNextProgramTimer(thedevice, thedeviceDict, thetimer, thevaluesDict):
    """ Update time regarding Next Program Data

        Args:
            thedevice: current EyeTV device
            thevaluesDict: dictionary of the status values so far
        Returns:
            success: True if success, False if not
    """
    core.logger(traceLog = "Working on timer data")

    # timer data
    theName = thevaluesDict['Title'] + u' - ' + thevaluesDict['Episode'] + u' ('+thevaluesDict['ChannelName'] + u')'
    theDescription = thevaluesDict['Title'] + u'\n' + thevaluesDict['Episode'] + u'\n' + thevaluesDict['ChannelName'] +u'\n' + thevaluesDict['StartTime'] + u'\n' + thevaluesDict['Duration'] + u' min'
    theAmount = datetime.strptime(thevaluesDict['StartTimestamp'], '%Y-%m-%d %H:%M:%S') - datetime.now()
    core.logger(traceLog = "Raw amount %s" % (theAmount))
    theAmount = theAmount.seconds/60 + theAmount.days*24*60 - int(thedeviceDict["PrepadTime"])

    if thetimer is None:
        # needs to create a timer device
        core.logger(traceLog = "Creating a new timer")
        thetimer = (indigo.device.create(protocol=indigo.kProtocol.Plugin,
                 name = theName.encode('ascii', 'ignore'),
                 description= theDescription.encode('ascii', 'ignore'),
                 pluginId="com.perceptiveautomation.indigoplugin.timersandpesters",
                 deviceTypeId="timer",
                 props={'amount':theAmount, 'amountType':'minutes'},
                 folder=thedevice.folderId))
        indigo.activePlugin.timerPlugin.executeAction("startTimer", deviceId=thetimer.id)

        # update device property
        localprops = thedevice.pluginProps
        localprops.update({"TimerDevice":thetimer.id})
        thedevice.replacePluginPropsOnServer(localprops)
        core.logger(msgLog = u'created new timer \"%s\" (id:%s) for %s minutes' % (theName,thetimer.id, theAmount))
    else:
        core.logger(traceLog = "Updating the timer")
        thetimer.name = theName.encode('ascii', 'ignore')
        thetimer.description = theDescription.encode('ascii', 'ignore')
        thetimer.replaceOnServer()
        indigo.activePlugin.timerPlugin.executeAction("setTimerStartValue", deviceId=thetimer.id, props={'amount':theAmount, 'amountType':'minutes'})
        indigo.activePlugin.timerPlugin.executeAction("startTimer", deviceId=thetimer.id)
        core.logger(msgLog = u'updated timer \"%s\" (id:%s) for %s minutes' % (theName,thetimer.id, theAmount))
