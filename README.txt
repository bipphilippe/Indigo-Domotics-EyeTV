###################################################################################
# EyeTV plug-in
# By Bernard Philippe (bip.philippe) (C) 2015
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.#
#
####################################################################################

Indigo Automation Plug-in for EyeTV and Turbo.264 HD

This plug-in allows to declare as devices : EyeTV application and Turbo.HD application.

For Turbo.HD:
- the status reflects what Turbo.264 HD is doing (Encoding, Stopped, Unavailable, Error)
- reflects the following application data as Indigo states
    - isEncoding: True if Turbo.264 is currently encoding, False if you can start a new encode.
    - isTurboHardwareIn: True if the Turbo.264 hardware is plugged in.
    - lastErrorCode: Last error code that occurred, e.g. during encoding.

For EyeTV:
- the status reflects what EyeTV is doing (Playing, Recording, Paused, Stopped, Unavailable, Error)
- reflects the following application data as Indigo states:
    - isCompacting: true if application is compacting a recording
    - isExporting: true if application is exporting a recording
    - isRecording: recording state of the application
    - isSavingClip: true if application is saving a clip as recording
    - isplaying: play state of the application
    - isBusy : any of the previous flag is true
    - AlertMenu: Is a modal fullscreen alert message open?
    - CurrentChannel: current channel name
    - isTurboHardwareIn: True if the Turbo.264 hardware is plugged in.
    - PlaybackVolume : playback volume
    - isMutedVolume : true is volume is muted
    - PostpadTime:	postpad time in minutes
    - PrepadTime: prepad time in minutes
    - isServerMode: boolean state whether EyeTV is still in server mode
- trace the next recording time (according program list) in the following states:
    - UniqueID : a number that identifies the program
    - ChannelName : recording channel name
    - Duration : scheduled duration
    - StartTime : scheduled start time
    - StartTimestamp : scheduled start time in a special format (internal use)
    - Title : program titlew
    - Episode : episode name or other informations (if not a TV sho)
- manages a self-created an updated timer that reflects the remaining time before the next recording time (minus the prepad time). The name of the timer changes according the program. A tipical use of the timer if to wake up the EyeTV drive and application before a recording (using the Mac System plug-in)
   
More on the indigo Forum : http://forums.indigodomo.com/viewtopic.php?f=162&t=13678
