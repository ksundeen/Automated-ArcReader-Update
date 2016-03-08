# Automating Copying/Updating of Remote Geodatabase for Remote Laptops for ArcReader.
# Created by Kim Sundeen 3/1/2016

"""
VERBOSE DESCRIPTION:
Python program automates the copy & export of an SDE enterprise
geodatabase for use in disconnected (no internet access) remote laptop environment.
Replication of the SDE geodatabase was not an option since the entire database was too
large; therefore we needed to select a subset of all feature datasets and feature classes
to copy into a PortableDuluth.gdb. This python program also automates copying, clipping,
& export of parcel layers for ownership. The script creates a track log of all procedures
completed with logging any errors as well as gives a script runtime.

# NEED FOR ARCREADER UPDATING PROJECT:
All field workers with laptops currently use the ArcReader map "TapNCurb" and need a current
copy of our in-network SQL Server SDE GIS Database with new utilities, ownership, & GPS points.
They sometimes have spotty internet connection and thus need a reliable disconnected map solution
to view updated utility and ownership data as soon as new data are available to help them locate
the City's utilities for Gopher State One Calls.

# OBSTACLES TO OVERCOME:
The map has normally only been updated every 1-3 months depending on when the field worker connects
their laptop to the City Network AND Mick Thorstad has updated the database holding all the GIS
data for the map. The GIS database has been an exported copy of the SQL Server SDE GIS database
that Richard and Al manage. In the past, Mick has exported all the tables needed for the remote
database every 1-3 months since it takes him 1-2 days to complete the database export process
manually; it's a lengthy and annoying manual update process.

# PROPOSED SOLUTION:
1)	Automate remote database export of GIS database
2)	Update the batch script that field workers run to copy the new remote database and TapNCurb.pmf
    map onto their laptops
3)	Work with IT to add a pop-up message on field worker's laptops that informs them if their
    database & map is more than 1 week old.
4)	In the future...Work with IT to possibly "push" the ArcReader map & database updates to remote
    worker's laptops, so field workers don't need to always bring their laptops into the office.
"""


import arcpy, os, shutil, logging, time, datetime
import gc #for garbage cleanup to clear memory
from arcpy import env

# Global Variables
startTimeSeconds = time.time() #sets a start time for code

# List output PortableGIS.gdb
arcpy.env.workspace = 'S:/GIS_Public/GIS_Data/MapDocuments/Published_Maps/ArcReaderRemoteUpdate/PortableDuluth.gdb/'

# Set a log file on local laptop to determine when ArcCatalog was last updated
## read last lines for when ArcReader was last updated
## track time when script starts
# Set up an Update Log file
def setLogger(__name__):
    """
    PURPOSE:
    Function creates a logger handler object to attach messages based on
    which function is running under the __main__ module.

    PARAMETERS:
    __name__ = reserved word for referencing the __main__ reserved word of each function.
    logfilepath = string of file location
    formatter = string reference of how output for each logging file will be returned in logfilepath
    """
    global logger
    logfilepath = r'S:\GIS_Public\Tools\Code\Python\ArcReaderExport\ProcessLogfile.log'
    logger = logging.getLogger(__name__) # __name__ refers to any module running (or function)
    logger.setLevel(logging.INFO)
    logger.propagate = True

    # create a logging file handler
    filehandler = logging.FileHandler(logfilepath)
    filehandler.setLevel(logging.INFO)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - Running Module: %(name)s; Line#: %(lineno)d} %(levelname)s |-| %(message)s')
    filehandler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(filehandler)
    # add logging header
    logger.info("""\n\n----------------Restart ArcReader export script----------------\n\n""")

setLogger(__name__)
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------

# Rename older file gdb to file gdb_old to allow a new file gdb to be created
## function = takes old file gdb name, renames, & outputs empty gdb

def createEmpytGDB(directoryPath='S:/GIS_Public/GIS_Data/MapDocuments/Published_Maps/ArcReaderRemoteUpdate/',
                   originalGDB='PortableDuluth.gdb',
                   backupNameGDB='PortableDuluth_backup.gdb'):
    """
    PURPOSE:
    Function takes existing geodatabase, makes a copy as a backup, then
    creates a new empty gdb with the original oldNameGDB's file name.

    PARAMETERS:
    directoryPath = string of file path; needs to use forward slashes '/'
    oldNameGDB = string of gdb name
    backupNameGDB = string of gdb name
    """
    arcpy.env.overwriteOutput = True
    
    currentdir = os.getcwd()
    print 'Current directory being checked: ' + directoryPath

    # test if any files end in oldNameGDB
    if arcpy.Exists(os.path.join(directoryPath, originalGDB)) == False:
        # create new empty gdb with original name
        arcpy.arcpy.CreateFileGDB_management(directoryPath, originalGDB)
        print 'Created new gdb {0}'.format(originalGDB)
        
    else:        
        for file in os.listdir(directoryPath):
                            
            if file.endswith(originalGDB):
                try:
                    # Check for PortableGIS_backup.gdb; if exists, delete
                    for anotherFile in os.listdir(directoryPath):                    
                        # Delete backup PortableGIS_backup.gdb to be replaced
                        if anotherFile.endswith(backupNameGDB):
                            shutil.rmtree(os.path.join(directoryPath,backupNameGDB))
                            print 'Removed ' + backupNameGDB
                            logger.info('Removed {0}'.format(backupNameGDB))
                            
                    # Compacts gdb & removes locks on gdb
                    arcpy.Compact_management((os.path.join(directoryPath, originalGDB)))
                    print 'Compacted ' + file
                    logger.info('Compacted {0}'.format(file))

                    # Renames existing PortableDuluth.gdb to "PortableDuluth_backup.gdb"
                    # Uses python's move function to move the directory of the geodatabase
                    shutil.move(os.path.join(directoryPath, originalGDB), os.path.join(directoryPath, backupNameGDB))
                    print'Renamed', originalGDB, 'to', backupNameGDB
                    logger.info('Renamed {0} to {1}'.format(originalGDB, backupNameGDB))

                    # Create new empty gdb with original name of 'PortableGIS.gdb'
                    arcpy.CreateFileGDB_management(directoryPath, originalGDB)
                    print 'Created new empty gdb: ' + file
                    logger.info('Created new empty GDB {0} in {1}'.format(originalGDB, directoryPath))

                            
                    # Clear memory
                    del anotherFile

                except shutil.Error as e:
                    print('Error: %s' % e)
                    logger.info('Error: %s' % e)
                except IOError as e:
                    print('Error: %s' % e.strerror)
                    logger.info('Error: %s' % e.strerror)       
                except:
                    print "Couldn't create empty GDB"
                    print arcpy.GetMessages()
                    logger.info('XXX Failed to create empty GDB in {0}'.format(directoryPath))
                    logger.error("Error in function createEmpytGDB.",exc_info=True)

            else:
                print 'other files: ' + file

        # Clear Memory
        del file

    # Clear Memory
    del directoryPath, originalGDB, backupNameGDB, currentdir
                

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
    
# Copy selected SDE geodatabase feature datasets into new file gdb.
def copyFeatureDatasets(fdList, toGDBpath):
    """
    PURPOSE:
    Function takes a list of feature datasets from another geodatabase, &
    copies them into another gdb.

    PARAMETERS:
    featureDatasetList = list of feature datasets to copy into new gdb.
    toGDBpath = the full file path to gdb, such as 'S:/GIS_Public/GIS_Data/MapDocuments/Published_Maps/ArcReaderRemoteUpdate/PortableDuluth.gdb'
    existingFCpath_SpatialRefFC = full file path to feature class with correct spatial reference to be used
        for new feature datasets being imported into new new gdb, such 
    """

    # All spatial reference will be the St Louis County Transverse Mercator System 96 (custom, feet).
    # the transformation process of converting any NAD83UTM 15N (feet) coordinates into the custom St Louis Cty system showed there is only
    # a +/- 0.001 foot difference in x & y coordinate positions when comparing the original GPS points (taken from +/- 0.2 foot survey-grade accurate
    # GPS points with the points that were referenced FROM the GPS points & digitized into NAD83UTM 15N (feet).
    # As a side note, the St Louis County Transverse Mercator System 96 (custom, feet) is the SAME as Esri's spatial reference system of
    # "NAD_1983_HARN_Adj_MN_St_Louis_CS96_Feet" (WKID = 103777); the spatial references for both these systems were compared and all numbers were exactly the same.

    # Can set default if not entered in function:   
    #toGDBpath = r'G:\PROJECTS\ArcReaderTest\PortableGIS.gdb'
    arcpy.env.overwriteOutput = True

    # Reference spatial reference of feature class      
    existingSpatRef = r'Database Connections\cihl-gisdat-01_sde_current_gisuser.sde\sde.SDE.GPS\sde.SDE.EngGPSPts'
    spatialRef = arcpy.Describe(existingSpatRef).spatialReference  # should be St. Louis County original coordinate system
    print 'Datasets will be copied using Spatial Reference:', str(spatialRef.name)

    try:
        # For each feature datasets in the fdList, create an empty feature dataset in the new PortableGDB
        # with St. Louis County Coordinate System (custom, feet)
        for fd in fdList:
            arcpy.CreateFeatureDataset_management(toGDBpath, fd, spatialRef) #spatialRef = St. Louis County Custom (feet) coordinate system)
            print 'Copied Feature Dataset into Gdb:', fd

        print 'Feature Datasets copied into', toGDBpath, ' with Spatial Reference of', spatialRef
        logger.info('Copied list of feature datasets into {0}, spatialRef = {1}'.format(toGDBpath, str(spatialRef.name)))

        # Also create a feature dataset for Rice Lake Township feature classes
        arcpy.CreateFeatureDataset_management(toGDBpath, 'Rice_Lake_Twnshp', spatialRef) #spatialRef = St. Louis County Custom (feet) coordinate system)
        print 'Copied Feature Dataset into Gdb:', 'Rice_Lake_Twnshp'

        # Clear memory
        del fd, fdList, toGDBpath, spatialRef, existingSpatRef

    except:
        logger.error("Error in function copyFeatureDatasets.",exc_info=True)

#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------

def copyFCtoFC(fromGDBpath, fdToFc_Dict, toGDBpath,
               gasGDBpath=r'S:\GIS_Public\GIS_Data\DefaultGDB\SDESchemaTest.gdb\Gas'):
    '''
    PURPOSE: Function takes a dictionary of keys (feature datasets) mapped to
    values (a list of feature classes) and copies each feature class to the
    mapped feature dataset in the out-geodatabase ('toGDBpath'). It essentially
    copies all feature classes from the original GDB to the new GDB.

    PARAMETERS:
    fromGDBpath = string of GDB from which feature classes will be copied.
    fdToFc_Dict = a crosswalk of feature dataset keys mapped to a list of all feature
    classes.
    toGDBpath = string of GDB to which feature classes will be copied. 
    '''
    arcpy.env.overwriteOutput = True

    try:
        # Iterate through dictionary
        for key, val in fdToFc_Dict.iteritems():

            outDatasetPath = os.path.join(toGDBpath, key)   # access the feature dataset name for where to copy all feature classes (val)

            for fc in val:

# Use code block when Richard's database update is official to grab new gas data.
##                # grabs only Gas dataset feature classes from Richard's new SDE Gas Schema file gdb
##                if fc[0:3] == 'gas':
##                    inFC = fromGDBpath + '\\' + key + '\\' + fc  # should grab all sde feature classes with those feature datasets except in a different gdb location
##                    
##                else:
##                    inFC = fromGDBpath + '\\sde.SDE.' + key + '\\sde.SDE.' + fc  # should grab all sde feature classes with those feature datasets except in a different gdb location
##                    
##                outFC = os.path.join(outDatasetPath, fc) # should copy sde feature classes to the remote gdb location

                inFC = fromGDBpath + '\\sde.SDE.' + key + '\\sde.SDE.' + fc  # should grab all sde feature classes with those feature datasets except in a different gdb location
                    
                outFC = os.path.join(outDatasetPath, fc) # should copy sde feature classes to the remote gdb location
                
                try:
                    # Execute FeatureClassToFeatureClass
                    arcpy.FeatureClassToFeatureClass_conversion(inFC, outDatasetPath, fc)
                    print 'Feature class successfully copied: ', fc
                    logger.info('Copied fc: {0} to fc: {1}'.format(inFC, outFC))
        
                except:
                    print 'Failed to copy from SDE dbs ({0}) to PortableGIS fc ({1})'.format(inFC, outFC)
                    logger.info('XXX Failed to copy from SDE dbs ({0}) to PortableGIS fc ({1})'.format(inFC, outFC))

        # Clear memory
        del fromGDBpath, fdToFc_Dict, toGDBpath


    except:
        print 'Failed to access feature classes or feature datasets in: {0} or {1}'.format(fromGDBpath, toGDBpath)
        print arcpy.GetMessages()
        logger.info('XXX Failed to access feature classes or feature datasets in: {0} or {1}'.format(fromGDBpath, toGDBpath))
        logger.error("Error in function copyFCtoFC.",exc_info=True)

      
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------

def copySingleFCtoFC(fromGDBpath, toGDBpath, fc):
    '''
    PURPOSE: Function takes specific feature class & copies into output GDB.

    PARAMETERS:
    fromGDBpath = string of GDB from which feature classes will be copied.
    fc = feature class to be copied.
    toGDBpath = string of GDB dataset to which feature classes will be copied. 
    '''
    arcpy.env.overwriteOutput = True
    inFC = os.path.join(fromGDBpath, fc)
    outFC = os.path.join(toGDBpath, fc)


    try:
        # tests if fc already exists, if it does, break out of loop.
        ##if arcpy.Exists(os.path.join(toGDBpath, fc)) == False:
        # Execute FeatureClassToFeatureClass
        arcpy.FeatureClassToFeatureClass_conversion(inFC, toGDBpath, fc)
        print 'Feature class successfully copied: ', fc
        logger.info('Copied fc: {0} to gdb'.format(fc))
        
        # Clear memory
        del fromGDBpath, fc, toGDBpath, outFC, inFC

    except:
        print 'Failed to access feature class of {0} in: {1} or {2}'.format(fc, fromGDBpath, toGDBpath)
        print arcpy.GetMessages()
        logger.info('XXX Failed to access feature classes or feature datasets in: {0} or {1}'.format(fromGDBpath, toGDBpath))
        logger.error("Error in function copyFCtoFC.",exc_info=True)
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------

# Copy County Assessors table
## table is already downloaded daily, then copy table over to PortabelGDB
## function = take copied table & copy into portableGDB
# Look up data needed in TapNCurb.MXD
def updateAssessorTable(toGDBpath):
    """
    PURPOSE:
    Function takes the SDE Assessor's table & copies it into another gdb.

    PARAMETERS:
    toGDBpath = string of file path to the output geodatabase (PortableGIS.gdb)
    assessorDBtable = string file path of the connection to St. Louis County's SDE database
    copiedAssessorTablePath = joined file path pf the 
    """
    try:
        ## Assessor's SDE table = r'cihl-DataBA-01_MCIS.sde  #username = reportuser; pw = granite
        # feature class = 'Assessor.dbo.vwGISParcel'

        assessorDBtable = r'Database Connections\cihl-databa-01_MCIS.sde\Assessor.dbo.vwGISParcel'
        copiedAssessorTablePath = os.path.join(toGDBpath, "Assessor")

        if arcpy.Exists(assessorDBtable) == False:
            arcpy.Copy_management(assessorDBtable, copiedAssessorTablePath)
        else:
            print 'Overwriting previous assessor table'
            arcpy.env.overwriteOutput = True
            arcpy.Copy_management(assessorDBtable, copiedAssessorTablePath)

            print 'Completed copy of {0}'.format(copiedAssessorTablePath, toGDBpath)
            logger.info("Copied updated Assessor's table into {0}".format(toGDBpath))

        # Clear memory
        del toGDBpath, assessorDBtable, copiedAssessorTablePath

    except:
        print "Couldn't update Assessor's table"
        print arcpy.GetMessages()
        logger.info("XXX Failed to copy updated Assessor's table into {0}. \nArcGIS Messages: {1}".format(toGDBpath, arcpy.GetMessages()))
        logger.error("Error in function updateAssessorTable.",exc_info=True)


#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------

 
# Automate clipping of County's Rice Lake townships; copy to new file gdb
def clipAndCopyRiceLakeFC(toGDB_RiceLake_path = 'S:/GIS_Public/GIS_Data/MapDocuments/Published_Maps/ArcReaderRemoteUpdate/PortableDuluth.gdb/Rice_Lake_Twnshp'):
    """
    PURPOSE:
    Function takes the Rice Lake Township outline & clips St. Louis County's
    updated data to the township ouline. Then it copies file to another gdb.

    PARAMETERS:
    featureOutline = Rice Lake Township boundary. 
    countyServData = string of database connection to St Louis County's SDE.
    toGDB_RiceLake_path = string of database connection to PortableGIS.gdb (or other) to copy feature to.

    **Default Portable GDB filepath is specified in function declaration-->replace with new location, if needed
    toGDB_RiceLake_path = 'S:/GIS_Public/GIS_Data/MapDocuments/Published_Maps/ArcReaderRemoteUpdate/PortableDuluth.gdb/Rice_Lake_Twnshp'
    """
    
    try:
        arcpy.env.overwriteOutput = True

        # if table exists, then copy into new GDB
        countyServDbs = 'Database Connections/slc_sde_viewer.sde/'

        if arcpy.Exists(countyServDbs) == True:

            # Set all database connections:
            rowsRiceLakeFCpath = countyServDbs + 'sde.STLOUIS.CDSTRL_ROW'
            streetsRiceLakeFCpath = countyServDbs + 'sde.STLOUIS.TRANS_RoadCenterlinesPW'
            parcelsRiceLakeFCpath = countyServDbs + 'sde.STLOUIS.CDSTRL_ParcelInfo'

            # Dictionary of County's filenames: new PortableGIS filename
            clipDict = {rowsRiceLakeFCpath: toGDB_RiceLake_path+'/RLT_ROW',
            streetsRiceLakeFCpath: toGDB_RiceLake_path+'/RLT_Streets',
            parcelsRiceLakeFCpath: toGDB_RiceLake_path+'/RLT_Parcels'
            }

            # Rice Lake Township clip area
            boundaryRiceLakeFC = 'S:/GIS_Public/GIS_Data/DefaultGDB/ArcReaderUpdate_files.gdb/RiceLakeTownshipClipBoundary'

            # Clip each layer to Rice Lake Clipped Boundary & Copy into PortableGIS.gdb
            # Automatically import feature classes into feature dataset with St. Louis County Coord. System (custom, feet).
            # Transformation error is negligable (see other documents to review transformation errors)
            for inLyr, outLyr in clipDict.iteritems():
                arcpy.Clip_analysis(inLyr, boundaryRiceLakeFC, outLyr)
                print 'Successfully clipped feature class: ({0}) by Rice Lake southern boundary ({1}) into PortableDuluth.gdb: ({2})'.format(inLyr, boundaryRiceLakeFC, outLyr)
                logger.info('Clipped {0} by {1} into {2}'.format(inLyr, boundaryRiceLakeFC, outLyr))

        else:
            print 'Cannot access St Louis County database {0}'.format(countyServDbs)
            logger.info("Failed to copy updated Rice Lake Township parcels into {0}".format(toGDB_RiceLake_path))

        # Clear memory
        del toGDB_RiceLake_path, countyServDbs

    except:
        print "Something failed with the clipping of Rice Lake Township features"
        print arcpy.GetMessages()
        logger.info("XXX Something failed with the clipping of Rice Lake Township features. \nArcGIS Messages: {1}".format(toGDB_RiceLake_path, arcpy.GetMessages()))
        logger.error("Error in function clipAndCopyRiceLakeFC.",exc_info=True)
   
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------

# Running all functions

#-------------------------------------------------------------------------------------------------------
##
### Test dictionary (less data)
##portableGISdict = {
##    'Buildings': [
##        'Buildings_DLH' 
##    ],
##
##    'LakeSuperior': [
##        'Lake',
##        'LakeNoIsland',
##        'Shoreline'
##    ],
##
##    # this dataset won't show feature classes in versions??
##    'Landuse': [
##        'Shoreland_Management_Zones'
##    ],
##
##    'Maintenance': [
##        'UtilityOps_PavementRestorationPts',
##        'UtilityOps_PavementRestoration'
##    ],
##
##    'GPS': [
##        'EngGPSPts'
##    ]
##}


# Dictionary for feature datasets with
portableGISdict = {
    'Buildings': [
        'Buildings_DLH' 
    ],

    'LakeSuperior': [
        'Lake',
        'LakeNoIsland',
        'Shoreline'
    ],

    # this dataset won't show feature classes in versions??
    'Landuse': [
        'Shoreland_Management_Zones'
    ],


    'Maintenance': [
        'UtilityOps_PavementRestorationPts',
        'UtilityOps_PavementRestoration'
    ],

    'GPS': [
        'EngGPSPts'
    ],

    'Streams': [
        'DuluthStream_cl',
        'DuluthStreams_Ortho',
        'wrmo',
        'floodplain_stlouisco'
    ],

    'DEM': [
        'dem_ctour10ft'
    ],

    'Streets': [
        'Streets_PM',
        'Streets_DouglasCO'
    ],

# Un-comment out feature classes when new SDE schema is used
    'Gas': [
        'gasMeterSetting'
        ,'gasCPRectifierCable'
        ,'gasShutDown_Section'
        ,'gasCPRectifier'
        ,'gasValve'
        ,'gasManholes'
        ,'gasCPTestPoint'
        ,'gasCPAnode'
        ,'gasDistribution_MainAnno'
        ,'gasValveAnno'
        ,'gasControllableFitting'
        ,'gasRegulatorStation'
        ,'GasPipeCasing'
        ,'gasNonControllableFitting'
        ,'gasTownBorderStation'
        ,'gasSection_ValveAnno'
        ,'gasDistributionMain'
        ,'GasServices'
        ,'gasVault'
        ,'gasTransmissionMain'
        ,'gasAbandonedGasPipe'
        #,'gasFuelLine'
        #,'gasValve_Bypass'
        #,'gasValve_EFV'
        #,'gasValve_Line'
        #,'gasValve_Regulator'
        #,'gasValve_Section'
        #,'gasValve_Service'  
    ],

    'Watersheds': [
        'Watersheds_DLH'
    ],

    'Cadastral': [
        'Curblines',
        'Boundary'
    ],

    'limits': [
        'engProjectAreas',
        'wgareas',
        'duluthbndline',
        'cityarea'
    ],

    'SteamSystem': [
        'SteamTraps',
        'SteamManholes',
        'SteamAnchors',
        'Meter_Address',
        'SteamLateral_Anno',
        'MeterBuildingParcel',
        'SteamCasings',
        'SteamMapBnd',
        'SteamAnodeWire',
        'SteamLateral',
        'SteamVault',
        'SteamMains',
        'SteamAnode',
        'SteamFittings',
        'SteamMain_Anno',
        'LeaderLines',
        'SteamValves'
    ],

    'SanitarySewerNetwork': [
        'ssAnnoLeaders',
        'ssAnno',
        'ssLateralLine',
        'ssMeter',
        'ssSystemValve',
        'ssControlValve',
        'ssFitting',
        'ssNetworkStructure',
        'ssGravityMain',
        'ssWyes',
        'ssPump',
        'ssManhole',
        'ssCleanOut',
        'ssDischargePoint',
        'ssPressurizedMain'
    ],

    'SanitarySewerFeatures': [
        'TracerBox'
    ],

    'Water_Distribution_Features': [
        'wUndergroundEnclosure',
        'wAnode',
        'wCasing',
        'wOperationalAreas',
        'wWaterStructure',
        'wInsulation'
    ],

    'Water_Distribution_Network': [
        'wFitting',
        'wNetworkStructure',
        'wControlValve',
        'wRegulatorStation',
        'wPressurizedMain',
        'wHydrant',
        'wServiceValves',
        'wLateralLine',
        'wGravityMainAnno',
        'wSystemValve',
        'wSystemValveAnno',
        'wGravityMain',
        'wManhole'
    ],

    'ParcelFeatures': [
        'LotAnno',
        'PLS_lines',
        'ROW',
        'corners_pls',
        'StreetName',
        'Subdivision',
        'BoundaryDLH',
        'survey_pts',
        'Block',
        'QuarterQuarter',
        'Sections',
        'Quarters',
        'Discrepancy_Pts',
        'Lots',
        'ParcelAnno',
        'Parcels'
    ],

    'StormSewerFeatures': [
        'stsCatchment',
        'stsConstruction',
        'stsBMP_Systems',
        'stsWaterStructure'
    ],

    'StormSewerNetwork': [
        'stsFitting',
        'stsAnnoCB',
        'stsNetworkStructure',
        'stsAnno',
        'stsAnnoLeaders',
        'stsInletsOutlets',
        'stsGravityMain',
        'stsSystemValve',
        'stsCatchBasin',
        'stsAnnoCBLeaders',
        'stsManhole',
        'stsPressurizedMain'
    ]

}
##
##
###-------------------------------------------------------------------------------------------------------
##
### Old Feature Dataset list from PortableGIS.gdb
##### feature dataset list from those already created in the PortableGIS.gdb
####fdList = ["Buildings" ,
####          "Cadastral" ,
####          "Contours" ,
####          "Duluth_Parcel_Data" ,
####          "Gas_Features" ,
####          "Lake_Features" ,
####          "Limits" ,
####          "Pavement_Mgmt" ,
####          "Permits",
####          "Rice_Lake_Tnshp" ,
####          "Sanitary_Features" ,
####          "Sanitary_Index_Pages" ,
####          "Shoreland_Management_Features" ,
####          "Steam_Features" ,
####          "Storm_Features" ,
####          "Storm_Network_Features" ,
####          "Streams" ,
####          "Street_Names" ,
####          "Streets" ,
####          "Water_Features" ,
####          "Water_Gas_Plat_Areas" ,
####          "Water_Network_Features"
####]

#----------------------------------------------------------------------------------------------------
# Set output geodatabase for functions to use (for the PortableDuluth.gdb)
portableGISpath = r'S:\GIS_Public\GIS_Data\MapDocuments\Published_Maps\ArcReaderRemoteUpdate\PortableDuluth.gdb'
#----------------------------------------------------------------------------------------------------


# 1. Run function to rename older file gdb to file gdb_old to allow a new file gdb to be created
createEmpytGDB(directoryPath = 'S:/GIS_Public/GIS_Data/MapDocuments/Published_Maps/ArcReaderRemoteUpdate/',
               originalGDB = 'PortableDuluth.gdb',
               backupNameGDB = 'PortableDuluth_backup.gdb')

#-------------------------------------------------------------------------------------------------------

# 2. Run function to copy selected SDE geodatabase feature datasets into new file gdb.
## Create list of keys from portableGISdict (above)
fdList = list(portableGISdict.keys())
copyFeatureDatasets(fdList = fdList, toGDBpath=portableGISpath)

#-------------------------------------------------------------------------------------------------------

# 3a. Run function to take dictionary of keys (feature datasets) mapped to values of feature classes &
# copies each feature class to mapped feature dataset in the out-geodatabase ('toGDBpath').
# not used: gasGDBpath=r'S:\GIS_Public\GIS_Data\DefaultGDB\SDESchemaTest.gdb\Gas'
copyFCtoFC(fromGDBpath = r'Database Connections\cihl-gisdat-01_sde_current_gisuser.sde',
           fdToFc_Dict = portableGISdict,
           toGDBpath=portableGISpath,
           gasGDBpath=portableGISpath)


# 3b. Run function to copy over "Sections_SLC" from a local gdb (in "GIS_Public\GIS_Data\DefaultGDB\ArcReaderUpdate_files.gdb")
# to PortableDuluth.gdb's "ParcelFeatures" dataset. This feature class is used for the SurveyParcelInfo.pmf
arcReaderDefaultGDBPath = 'S:/GIS_Public/GIS_Data/DefaultGDB/ArcReaderUpdate_files.gdb'
portableGIS_ParcelFeatures_path = 'S:/GIS_Public/GIS_Data/MapDocuments/Published_Maps/ArcReaderRemoteUpdate/PortableDuluth.gdb/ParcelFeatures'
copySingleFCtoFC(fromGDBpath=arcReaderDefaultGDBPath, toGDBpath=portableGIS_ParcelFeatures_path, fc='Sections_SLC')
#-------------------------------------------------------------------------------------------------------

# 4. Run function to copy County Assessors table into PortableGIS.gdb
updateAssessorTable(toGDBpath=portableGISpath)

#-------------------------------------------------------------------------------------------------------

# 5. Run function to clip St. Louis County's Rice Lake townships & copy to PortableGIS.gdb
clipAndCopyRiceLakeFC(toGDB_RiceLake_path = 'S:/GIS_Public/GIS_Data/MapDocuments/Published_Maps/ArcReaderRemoteUpdate/PortableDuluth.gdb/Rice_Lake_Twnshp')

#-------------------------------------------------------------------------------------------------------



elapsedTimeSeconds = time.time() - startTimeSeconds # outputs elapsed time since beginning of script
elapsedTimeMinutes = elapsedTimeSeconds/60.0

#------Script End------------------------------------------------------------------------------
print "----------------------------------------------"
print "\nScript completed in {0:0.2f} minutes (or {1:.2f} seconds)\nReview database located: {2}".format(elapsedTimeMinutes, elapsedTimeSeconds, arcpy.env.workspace)
print "----------------------------------------------"
logger.info("\n----------\nScript completed in {0:0.2f} minutes. \nReview database located: {1}.".format(elapsedTimeMinutes, arcpy.env.workspace))

# Delete logger file from memory
del logger

# Clear python console log's memory
clear = lambda: os.system('cls')
clear()

# Run Garbage Collectio to empty memory
gc.collect()
#-------------------------------------------------------------------------------------------------------       

