# $Header$
__RCSID__ = "$Id$"

import sys
import getopt

from DIRAC import gLogger
from DIRAC import S_OK, S_ERROR

from DIRAC.ConfigurationSystem.Client.ConfigurationData import gConfigurationData
from DIRAC.ConfigurationSystem.private.Refresher import gRefresher
from DIRAC.ConfigurationSystem.Client.PathFinder import getServiceSection

class UserConfiguration:

  def __init__( self, defaultSectionPath = "" ):
    self.currentSectionPath = defaultSectionPath
    self.mandatoryEntryList = []
    self.optionalEntryList = []
    self.commandOptionList = []
    self.__registerBasicOptions()
    self.isParsed = False
    self.componentName = "Unknown"
    self.loggingSection = "/DIRAC"

  def __getAbsolutePath( self, optionPath ):
    if optionPath[0] == "/":
      return optionPath
    else:
      return "%s/%s" % ( self.currentSectionPath, optionPath )

  def addMandatoryEntry( self, optionPath ):
    self.mandatoryEntryList.append( self.__getAbsolutePath( optionPath ) )

  def addOptionalEntry( self, optionPath, value ):
    self.optionalEntryList.append( ( self.__getAbsolutePath( optionPath ),
                                     str( value ) ) )

  def setOptionValue( self, optionPath, value ):
    gConfigurationData.setOptionInCFG( self.__getAbsolutePath( optionPath ),
                                       str( value ) )

  def __registerBasicOptions( self ):
    self.registerCmdOpt( "o", "option", "Option=value to add",
                         self.__setOptionByCmd  )
    self.registerCmdOpt( "s", "section", "Section to add an option",
                         self.__setSectionByCmd )
    self.registerCmdOpt( "h", "help", "Shows this help",
                         self.__showUsage )

  def registerCmdOpt( self, shortOption, longOption, helpString, function ):
    self.commandOptionList.append( ( shortOption, longOption, helpString, function ) )

  def getPositionalArguments( self ):
    if not self.isParsed:
      self.__parseCommandLine()
    return self.commandArgList

  def loadUserData(self):
    if not self.isParsed:
      self.__parseCommandLine()
    try:
      for optionTuple in self.optionalEntryList:
        gConfigurationData.setOptionInCFG( optionTuple[0], optionTuple[1] )

      retVal = self.__addUserDataToConfiguration()
      gLogger.initialize( self.componentName, self.loggingSection )
      if not retVal[ 'OK' ]:
        return retVal

      retVal = self.__getRemoteConfiguration()
      if not retVal[ 'OK' ]:
        return retVal

      isMandatoryMissing = False
      for optionPath in self.mandatoryEntryList:
        if not gConfigurationData.extractOptionFromCFG( optionPath ):
          gLogger.fatal( "Missing mandatory option in the configuration", optionPath )
          isMandatoryMissing = True
      if isMandatoryMissing:
        return S_ERROR()
    except Exception, e:
      gLogger.exception()
      gLogger.error( "Error while loading user specified configuration data", str( e ) )
      return S_ERROR()
    return S_OK()


  def __parseCommandLine( self ):
    gLogger.debug( "Parsing command line" )
    shortOption = ""
    longOptionList = []
    for optionTuple in self.commandOptionList:
      if shortOption.find( optionTuple[0] ) < 0:
        shortOption += "%s:" % optionTuple[0]
      else:
        gLog.warn( "Short option -%s has been already defined" % optionTuple[0] )
      if not optionTuple[1] in longOptionList:
        longOptionList.append( "%s=" % optionTuple[1] )
      else:
        gLog.warn( "Long option --%s has been already defined" % optionTuple[1] )

    try:
      opts, args = getopt.gnu_getopt( sys.argv[1:], shortOption, longOptionList )
    except getopt.GetoptError, v:
      # print help information and exit:
      gLog.fatal( "Error when parsing command line arguments: %s" % str( v ) )
      self.__showUsage()
      sys.exit(2)

    self.AdditionalCfgFileList = [ arg for arg in args if arg[-4:] == ".cfg" ]
    self.commandArgList = [ arg for arg in args if not arg[-4:] == ".cfg" ]
    self.parsedOptionList = opts
    self.isParsed = True

  def __addUserDataToConfiguration( self ):
    if not self.isParsed:
      self.__parseCommandLine()

    errorsList = []

    for fileName in self.AdditionalCfgFileList:
      retVal = gConfigurationData.loadFile( fileName )
      if not retVal[ 'OK' ]:
        errorsList.append( retVal[ 'Message' ] )

    for optionName, optionValue in self.parsedOptionList:
      optionName = optionName.replace( "-", "" )
      for definedOptionTuple in self.commandOptionList:
        if optionName == definedOptionTuple[0] or optionName == definedOptionTuple[1]:
          retVal = definedOptionTuple[3]( optionValue )
          if not retVal[ 'OK' ]:
            errorsList.append( retVal[ 'Message' ] )

    if len( errorsList ) > 0:
      return S_ERROR( "\n%s" % "\n".join( errorsList ) )
    return S_OK()

  def __getRemoteConfiguration( self ):
    needCSData = True
    if self.currentSectionPath == getServiceSection( "Configuration/CServer" ):
      if gConfigurationData.isMaster():
        gLogger.debug( "CServer is Master!" )
        needCSData = False
      else:
        gLogger.debug( "CServer is slave" )
    if needCSData:
      retDict = gRefresher.forceRefreshConfiguration()
      if not retDict['OK']:
        gLogger.fatal( retDict[ 'Message' ] )
        return S_ERROR()

    return S_OK()

  def setServerSection( self, serviceName ):
    self.componentName = serviceName
    self.currentSectionPath = getServiceSection( serviceName )
    self.loggingSection = self.currentSectionPath
    return self.currentSectionPath

  def __setSectionByCmd( self, value ):
    if value[0] != "/":
      return S_ERROR( "%s is not a valid section. It should start with '/'" % value )
    self.currentSectionPath = value
    return S_OK()

  def __setOptionByCmd( self, value ):
    valueList = [ sD.strip() for sD in value.split("=") if len( sD ) > 0]
    if len( valueList ) <  2:
      # FIXME: in the method above an exception is raised, check consitency
      return S_ERROR( "-o expects a option=value argument.\nFor example %s -o Port=1234" % sys.argv[0] )
    self.setOptionValue( valueList[0] , valueList[1] )
    return S_OK()

  def __showUsage( self ):
    gLogger.info( "Usage:" )
    gLogger.info( "  %s (<options>|<cfgFile>)*" % sys.argv[0] )
    gLogger.info( "Options:" )
    for optionTuple in self.commandOptionList:
      gLogger.info( "  -%s  --%s  :  %s" % optionTuple[:3] )
    return S_OK()

