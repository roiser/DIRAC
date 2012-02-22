#!/usr/bin/env python

########################################################################
# $HeadURL:  
# File :    dirac-accounting-encode-plotdict
# Author :  Stefan Roiser
########################################################################

"""
Encode Accounting plots from a dictionary provided e.g. by dirac-accounting-decode-fileid
"""

__RCSID__ = "$Id: $"

import datetime
import sys
from DIRAC import gLogger
from DIRAC.Core.Base import Script
from DIRAC.AccountingSystem.private.FileCoding import codeRequestInFileId

dict()

Script.setUsageMessage( '\n'.join( [ __doc__.split( '\n' )[1],
                                     'Usage:',
                                     '  %s [option|cfgfile] ... dict ...' % Script.scriptName,
                                     'Arguments:'
                                     '  dict: one or more python dictionaries passed as string, syntax conforming to the output of dirac-accounting-decode-fileid']))

Script.parseCommandLine()

plotDicts = Script.getPositionalArgs()

for plotDict in plotDicts:
  eDict = eval(plotDict)

  result = codeRequestInFileId( eDict )
  if not result[ 'OK' ]:
    gLogger.error( "Could not encode dictionary '%s', error was %s" % ( eDict, result[ 'Message' ] ) )
    sys.exit( 1 )
  gLogger.notice( "Encoding for dictionary '%s' is:\n\n%s" % ( eDict,  result[ 'Value' ] ) )

sys.exit( 0 )

