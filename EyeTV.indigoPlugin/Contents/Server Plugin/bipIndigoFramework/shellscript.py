#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################################################################################
""" shell script runner for Indigo plugins

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

import subprocess
import indigo
import core

########################################
def run(pscript, rule, akeys):
    """ Calls shell script and returns the result

        Args:
            pscript: shell script as text
            rule: separator string,
                  or list of tupples (firstchar,lastchar) to cut the string (trim will be applied),
                  or None for no action on text
            akeys: list or keys, ordered the same way that output data of the applescript,
                   or None
        Returns:
            python dictionnay of the states names and values,
            or unicode string returned by the script is akeys is None,
            or None if error
    """

    core.logger(traceRaw = u"going to call shell %s" % (pscript), traceLog = u"going to call shell %s..." % (pscript[:16]))

    p = subprocess.Popen(pscript,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,
                           shell=True,
                           close_fds=True)
    indigo.activePlugin.sleep(0.5)
    (pvalues, perror) = p.communicate()

    if len(perror)>0:
        # test if error
        core.logger(errLog = u"shell script failed because %s" % (perror.decode('utf-8')))
        return None

    if akeys is None:
        # return text if no keys
        returnvalue = pvalues.strip().decode('utf-8')
    elif rule is None:
        returnvalue= {akeys[0]: pvalues.strip().decode('utf-8')}
    elif type(rule) is list:
        # cut in slices
        returnvalue = {}
        for thekey,(firstchar,lastchar) in dict(zip(akeys,rule)).iteritems():
            returnvalue[thekey] = core.strutf8(pvalues[firstchar:lastchar].strip())
    else:
        # just use split
        returnvalue = dict(zip(akeys,pvalues.split(rule)))
        for thekey,thevalue in pvalues.iteritems():
            returnvalue[thekey] = core.strutf8(thevalue.strip())

    core.logger(traceRaw = u"returned from shell: %s" % returnvalue, traceLog = u"returned from shell %s..." % (pscript[:16]))

    return returnvalue


