#!/usr/bin/env python
########################################################################
# $HeadURL:  $
########################################################################
__RCSID__   = "$Id: $"
__VERSION__ = "$Revision: 1.1 $"
import sys,os
import DIRAC
from DIRAC import gLogger
from DIRAC.Core.Base import Script

fcType = 'LFC'
Script.registerSwitch( "f:", "file-catalog=","   Catalog client type to use")
Script.parseCommandLine( ignoreErrors = False )
for switch in Script.getUnprocessedSwitches():
  if switch[0].lower() == "f" or switch[0].lower() == "file-catalog":
    fcType = switch[1]

from DIRAC.DataManagementSystem.Client.FileCatalogClientCLI import FileCatalogClientCLI

if fcType == "LFC":
  from DIRAC.Resources.Catalog.LcgFileCatalogProxyClient import LcgFileCatalogProxyClient
  cli = FileCatalogClientCLI(LcgFileCatalogProxyClient())
  print "Starting LFC Proxy FileCatalog client"
  cli.cmdloop() 
elif fcType == "DiracFC":
  from DIRAC.DataManagementSystem.Client.FileCatalogClient import FileCatalogClient
  cli = FileCatalogClientCLI(FileCatalogClient())
  print "Starting DIRAC FileCatalog client"
  cli.cmdloop()  
else:
  print "Unknown catalog type", catype

