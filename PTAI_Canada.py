# Created 27.04.2018 by Yulmetova Maria, student-assistant at the Walkabilly lab, Memorial University of Newfoundland

#A flow chart is attached to visualize the algorithm


import urllib2
import zipfile
import arcpy
from arcpy import env
import os
import pandas as pd
import csv
import sys
import json
from arcpy.sa import *
arcpy.CheckOutExtension("3D")


def getGDBtable(txtFileName, gdbTableName,linkNumber):                             #Get GDBtable from txt-file (stop_times, trips and routes)
    print("Creating a new gdb-table for "+str(txtFileName))
    ispy3 = sys.version_info >= (3, 0)
    if ispy3:
        f = open(txtFileName, encoding="utf-8-sig")
    else:
        f = open(txtFileName)
    reader = csv.reader(f)
    # Convert everything in utf-8 to handle BOMs and weird characters.
    # Eliminate blank rows (extra newlines) while we're at it.
    if ispy3:
        columns = [name.strip() for name in next(reader)]
    else:
        columns = [name.decode('utf-8-sig').strip() for name in next(reader)]
    # Truncate the long field names.
    columns = [c[0:10] for c in columns]
    # Create a new Table
    gdbTable = arcpy.CreateTable_management(gdb, gdbTableName)
    # Add the appropriate fields to the new table; Hard-wire all the columns to be text values
    for col in columns:
        arcpy.AddField_management(gdbTable, col, "TEXT")
    # Write the data to the new table
    fields = columns
    with arcpy.da.InsertCursor(gdbTable, fields) as cur:
        for row in reader:
            cur.insertRow(row)

    arrival_time="arrival_ti"
    route_type="route_type"
    field_trip_headsign = "trip_heads"

    if arrival_time in fields:                                         #For stop_times table: select stop_times from 7am to 9am
        arcpy.TableToTable_conversion(gdbTable, gdb, "stoptime79_L"+str(linkNumber),
                                                 "(\"arrival_ti\" >='07:00:00' AND \"arrival_ti\" <='09:00:00')OR (\"arrival_ti\" >='7:00:00' AND \"arrival_ti\" <='9:00:00')OR (\"arrival_ti\" >=' 7:00:00' AND \"arrival_ti\" <=' 9:00:00')")
        print("A new table of all stop times from 7 am to 9 am has been created.")
    if route_type in fields:                                            #For routes table: created several tables for each mode
        arcpy.TableToTable_conversion(gdbTable, gdb, "route_type_0_L"+str(linkNumber), "route_type = '0'")     #0 - Tram, Streetcar, Light rail.
        arcpy.TableToTable_conversion(gdbTable, gdb, "route_type_1_L"+str(linkNumber), "route_type = '1'")     #1 - Subway, Metro.
        arcpy.TableToTable_conversion(gdbTable, gdb, "route_type_2_L"+str(linkNumber), "route_type = '2'")     #2 - Rail.
        arcpy.TableToTable_conversion(gdbTable, gdb, "route_type_3_L"+str(linkNumber),"route_type = '3'")      #3 - Bus.
        arcpy.TableToTable_conversion(gdbTable, gdb, "route_type_4_L" + str(linkNumber),"route_type = '4'")    #4 - Ferry.
                                                                                                               #5 - Cable car.
                                                                                                               #6 - Gondola, Suspended cable car.
                                                                                                               #7 - Funicular.
        print("Tables for each route types have been created")


def joinField(in_data,in_field,join_table,join_field,fieldName):
    arcpy.JoinField_management (in_data, in_field, join_table, join_field,fieldName)
    print("The "+str(fieldName)+" has been added to the "+str(in_data))

def tableToTable(in_rows,tableName,where_clause):
    arcpy.TableToTable_conversion(in_rows, gdb, tableName,where_clause)

def frequencyAnalysis (in_table, out_table, frequency_fields):
    arcpy.Frequency_analysis(in_table, out_table,frequency_fields)
    print("Frequency analysis has been completed.")


def txtToPoints(txtfile,featureName):
    max_stop_desc_length = 250
    print("2. Reading input stops.txt file...")
    ispy3 = sys.version_info >= (3, 0)
    if ispy3:
        f = open(txtfile, encoding="utf-8-sig")
    else:
        f = open(txtfile)
    reader = csv.reader(f)
    # Convert everything in utf-8. Eliminate blank rows.
    reader = ([x.decode('utf-8-sig').strip() for x in r] for r in reader if len(r) > 0)
    # The first row contains column names:
    columns = [name.strip() for name in next(reader)]
    # Check the stops.txt file for the correct fields: Make sure lat/lon values are present
    if "stop_lat" not in columns:
        arcpy.AddError(
            "Your stops.txt file does not contain a 'stop_lat' field. Please choose a valid stops.txt file.")
        print ('error')
    if "stop_lon" not in columns:
        arcpy.AddError(
            "Your stops.txt file does not contain a 'stop_lon' field. Please choose a valid stops.txt file.")
        print ('error')
    if "stop_id" not in columns:
        arcpy.AddError(
            "Your stops.txt file does not contain a 'stop_id' field. Please choose a valid stops.txt file.")
        print ('error')
    # Find indices of stop_lat and stop_lon columns
    stop_lat_idx = columns.index("stop_lat")
    stop_lon_idx = columns.index("stop_lon")
    stop_id_idx = columns.index("stop_id")
    # Truncate the long field names at 10 characters.
    columns = [c[0:10] for c in columns]
    # Create new feature class and add the corresponding fields; Hard-wire all the columns to be text values
    stopsfeature = arcpy.CreateFeatureclass_management(gdb, featureName, "POINT")
    for col in columns:
        arcpy.AddField_management(stopsfeature, col, "TEXT")
    # Write the stops.txt data to the new feature class
    print("Writing the stops.txt data to the new feature class...")
    try:
        fields_stops = ["SHAPE@"] + columns
        with arcpy.da.InsertCursor(stopsfeature, fields_stops) as cur:
            for row in reader:
                stop_id = row[stop_id_idx]
                # Get the lat/lon values. If float conversion fails, there is a problem
                try:
                    stop_lat = float(row[stop_lat_idx])
                except ValueError:
                    msg = 'stop_id "%s" contains an invalid non-numerical value \
    for the stop_lat field: "%s". Please double-check all lat/lon values in your \
    stops.txt file.' % (stop_id, str(row[stop_lat_idx]))
                    arcpy.AddError(msg)
                    raise
                try:
                    stop_lon = float(row[stop_lon_idx])
                except ValueError:
                    msg = 'stop_id "%s" contains an invalid non-numerical value \
    for the stop_lon field: "%s". Please double-check all lat/lon values in your \
    stops.txt file.' % (stop_id, str(row[stop_lon_idx]))
                    arcpy.AddError(msg)
                    raise
                    # Check that the lat/lon values are in the right range.
                if not (-90.0 <= stop_lat <= 90.0):
                    msg = 'stop_id "%s" contains an invalid value outside the \
    range (-90, 90) the stop_lat field: "%s". stop_lat values must be in valid WGS 84 \
    coordinates.  Please double-check all lat/lon values in your stops.txt file.\
    ' % (stop_id, str(stop_lat))
                    arcpy.AddError(msg)
                if not (-180.0 <= stop_lon <= 180.0):
                    msg = 'stop_id "%s" contains an invalid value outside the \
    range (-180, 180) the stop_lon field: "%s". stop_lon values must be in valid WGS 84 \
    coordinates.  Please double-check all lat/lon values in your stops.txt file.\
        ' % (stop_id, str(stop_lon))
                    arcpy.AddError(msg)
                if "stop_desc" in columns:
                    stop_desc_idx = columns.index("stop_desc")
                    if row[stop_desc_idx]:
                        # Truncate stop_desc, so it fits in the field length.
                        row[stop_desc_idx] = row[stop_desc_idx][:max_stop_desc_length]

                pt = arcpy.Point()
                pt.X = float(stop_lon)
                pt.Y = float(stop_lat)
                # GTFS stop lat/lon is written in WGS84
                ptGeometry = arcpy.PointGeometry(pt, WGSCoords)
                if output_coords != WGSCoords:
                    ptGeometry = ptGeometry.projectAs(output_coords)
                cur.insertRow((ptGeometry,) + tuple(row))
        print("Stops.shp has been created.Link:"+str(linkNumber))
    except Exception as err:
        arcpy.AddError("Error writing stops.txt data to feature class.")
        raise

def bufferAnalysis(points,stopsBufferPath,buffer_distance):
    arcpy.Buffer_analysis(points, stopsBufferPath, buffer_distance, "FULL", "ROUND", "ALL", "", "PLANAR")

def spatialJoinSUM(targetFeatures,joinFeatures,output,joinFeaturesfields):
    # Output will be the target features with SUM of joinFeatures fields
    # Create a new fieldmappings and add the two input feature classes.
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(targetFeatures)
    fieldmappings.addTable(joinFeatures)
    efcount=0
    for joinFeaturesfield in joinFeaturesfields:
        newfield = fieldmappings.findFieldMapIndex(joinFeaturesfield)
        fieldmap = fieldmappings.getFieldMap(newfield)
        # Get the output field's properties as a field object
        field = fieldmap.outputField
        # Rename the field and pass the updated field object back into the field map: 0=areas, 1=population
        field.name = "sum"+str(efcount)
        field.aliasName = "sum"+str(efcount)
        fieldmap.outputField = field
        # Set the merge rule to mean
        fieldmap.mergeRule = "Sum"
        fieldmappings.replaceFieldMap(newfield, fieldmap)
        efcount=efcount+1
        # Run the Spatial Join tool
    arcpy.SpatialJoin_analysis(targetFeatures, joinFeatures,output, "#", "#", fieldmappings)

def calculatePTAI(fc):
    arcpy.AddField_management(fc, "PTAI", "DOUBLE", "10", "4", "", "", "NULLABLE", "NON_REQUIRED", "")
    field1 = "PTAI"
    cursor = arcpy.UpdateCursor(fc)
    for row in cursor:
        field2 = row.getValue(PDratioFieldName)
        field3 = row.getValue('WEF')
        if (field2 == " ") or (field2 == 0) or (field2 == None) or (field3 == " ") or (field3 == 0) or (field3 == None):
            field2 = row.getValue(PDratioFieldName)
            field3 = row.getValue('WEF')
            row.setValue(field1, field3)
            cursor.updateRow(row)
        else:
            row.setValue(field1, field3 * field2)
            cursor.updateRow(row)
    print('PTAI has been calculated for CT')

def spatialJoinCTsum(targetFeatures,joinFeatures, output):
    # Create a new fieldmappings and add the two input feature classes.
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(targetFeatures)
    fieldmappings.addTable(joinFeatures)
    EFs=["EF0","EF1","EF2","EF3"]
    efcount=0
    for singleEF in EFs:
        # First get the EF fieldmap. EF is a field in the PointWalkWait.
        # The output will have the CTs/DAs with the attributes of the PointWalkWait.
        EF = fieldmappings.findFieldMapIndex(singleEF)
        fieldmap = fieldmappings.getFieldMap(EF)
        # Get the output field's properties as a field object
        field = fieldmap.outputField
        # Rename the field and pass the updated field object back into the field map
        field.name = "EFsum_"+str(efcount)
        field.aliasName = "EFsum_"+str(efcount)
        fieldmap.outputField = field
        # Set the merge rule to mean
        fieldmap.mergeRule = "Sum"
        fieldmappings.replaceFieldMap(EF, fieldmap)
        efcount=efcount+1
        # Run the Spatial Join tool, using the defaults for the join operation and join type
    arcpy.SpatialJoin_analysis(targetFeatures, joinFeatures, output, "#", "#", fieldmappings)












#Input Variables:
output_dir='./output'
input_dir="./input"
da=os.path.join(input_dir,"DAinCT_CanadaEqD.shp")       #Dissemination areas
CT=os.path.join(input_dir,"CT_CanadaEqD.shp")           #Census tracts
origins = os.path.join(input_dir,'pccf_inCTEQd.shp')    #Points of interests
pccfIDfield="pccfID"                                    #The ID field of the pccf_inCTEQd.shp (that are used as POI)
network = os.path.join(input_dir,'roadsCanadaEqD_ND.nd')#Network dataset

#Txt-files from TransitFeeds.com
stop_times = os.path.join(output_dir, 'stop_times.txt')
trips = os.path.join(output_dir, "trips.txt")
routes = os.path.join(output_dir, "routes.txt")
stops=os.path.join(output_dir,'stops.txt')

#GTFS stop lat/lon is written in WGS1984
WGSCoords = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984', \
    SPHEROID['WGS_1984',6378137.0,298.257223563]], \
    PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]; \
    -400 -400 1000000000;-100000 10000;-100000 10000; \
    8.98315284119522E-09;0.001;0.001;IsHighPrecision"
output_coords = WGSCoords
#Distances should be calculated in equidistant projection
EqD_CS="PROJCS['North_America_Equidistant_Conic',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Equidistant_Conic'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-96.0],PARAMETER['Standard_Parallel_1',20.0],PARAMETER['Standard_Parallel_2',60.0],PARAMETER['Latitude_Of_Origin',40.0],UNIT['Meter',1.0]]"


#Create a geodatabase where data will be stored
gdb=arcpy.CreateFileGDB_management(output_dir, "gtfs.gdb")
gdb="./output/gtfs.gdb"


#Output files names:
PTAI_CT = os.path.join(gdb,"PTAI_CT_")
PTAI_DA = os.path.join(gdb,"PTAI_DA")

#Intermediate output files names or/and their fields names
PDratioCT = os.path.join(gdb,"PDratioCT")
PDratioFieldName="PDratio"


### STEP 1 (CHECK THE FLOWCHART IN THE PDF)
#Get links that have to be downloaded
response = urllib2.urlopen('https://api.transitfeeds.com/v1/getLocations?key=b1b09e11-f0f6-40a0-9846-766bdc72cf28')
data = json.load(response)
locations=data["results"]["locations"]
links = []
for_t=0
for indexinlocations in locations:
   t = data["results"]["locations"][for_t]["t"]       #t=locations names
   #print(t)
   if "Canada" in t:
      id = data["results"]["locations"][for_t]["id"]
      #print("ID is "+str(id))
      getFeed = urllib2.urlopen(
         "https://api.transitfeeds.com/v1/getFeeds?key=b1b09e11-f0f6-40a0-9846-766bdc72cf28&location=" + str(
            id) + "&descendants=1&page=1&limit=100")
      getFeedData = json.load(getFeed)
      #print(getFeedData)
      feeds=getFeedData["results"]["feeds"]
      #print ("FEEDS:"+str(feeds))
      for_ty=0
      for indexinFeeds in feeds:
            ty=getFeedData["results"]["feeds"][for_ty]["ty"]
            #print("TYPE="+str(ty))
            if ty=="gtfs":
               try:
                   zipLink = getFeedData["results"]["feeds"][for_ty]["u"]["d"]
                   #print(zipLink)
                   links.append(zipLink)
               except:
                   checkid = getFeedData["results"]["feeds"][for_ty]["id"]
                   #print ("The "+str(checkid+"does not have gtfs data (.zip)"))
                   print(arcpy.GetMessages(2))
                   continue


            for_ty=for_ty+1
   for_t=for_t+1
#print("links: " + str(links))
#print len(links)
#Get the list of links without duplicates:
linksToDownload=list(set(links))
print("Links to download = "+str(linksToDownload))
print len(linksToDownload)


#Create empty lists for each mode where all the bus stops shape files (points) will be stored:
mode0 = []  #0 - Tram, Streetcar, Light rail.
mode1 = []  #1 - Subway, Metro.
mode2 = []  #2 - Rail.
mode3 = []  #3 - Bus.
mode4 = []  #4 - Ferry.
#Modes that were not used:
#5 - Cable car.
#6 - Gondola, Suspended cable car.
#7 - Funicular.

linkNumber=0
for url in linksToDownload[10:20]:
    try:
        #Dowload a zip-file and unzip it
        urlToOpen = urllib2.urlopen(url)
        with open("gtfs.zip", "wb") as code:
            code.write(urlToOpen.read())
        try:
            with zipfile.ZipFile("gtfs.zip", "r") as zip_ref:
                zip_ref.extractall(output_dir)
            print(str(linkNumber) + "-----" + "GTFS data has been downloaded from LINK " + str(url))
        except:
            print(arcpy.GetMessages(2))
            continue


        ### STEP 2 (CHECK THE FLOWCHART IN THE PDF).
        #Convert stops_time.txt, routes.txt and trips.txt into GDB-tables
        stops_timeTableName = 'stops_timeTable_L' + str(linkNumber)
        tripsTableName = "tripsTable_L" + str(linkNumber)
        routesTableName = "routesTable_L" + str(linkNumber)

        getGDBtable(stop_times, stops_timeTableName, linkNumber)
        getGDBtable(trips, tripsTableName, linkNumber)
        getGDBtable(routes, routesTableName, linkNumber)

        ### STEP 3 (CHECK THE FLOWCHART IN THE PDF).
        # Convert stops.txt to a shape-file
        stopsfeatureName = 'stops_L' + str(linkNumber)
        txtToPoints(stops, stopsfeatureName)

        tripsTable = os.path.join(gdb, tripsTableName)
        stopsfeature = os.path.join(gdb, stopsfeatureName)
        stop_time_79 = os.path.join(gdb, "stoptime79_L" + str(linkNumber))
        route_type_0 = os.path.join(gdb, "route_type_0_L" + str(linkNumber))
        route_type_1 = os.path.join(gdb, "route_type_1_L" + str(linkNumber))
        route_type_2 = os.path.join(gdb, "route_type_2_L" + str(linkNumber))
        route_type_3 = os.path.join(gdb, "route_type_3_L" + str(linkNumber))
        route_type_4 = os.path.join(gdb, "route_type_4_L" + str(linkNumber))
        route_type_list = [route_type_0, route_type_1, route_type_2, route_type_3,route_type_4]

        k = 0
        for mode in route_type_list:
            ### STEP 4 (CHECK THE FLOWCHART IN THE PDF).
            joinField(tripsTable, 'route_id', mode, 'route_id', "route_type")
            joinField(stop_time_79, "trip_id", tripsTable, "trip_id", "route_type")
            stop_times79_for_Name = "stop_times79_for_" + str(k) + "_L" + str(linkNumber)
            tableToTable(stop_time_79, stop_times79_for_Name, "\"route_type\" IS NOT NULL")
            stop_times79_for_ = os.path.join(gdb, stop_times79_for_Name)
            ### STEP 5 (CHECK THE FLOWCHART IN THE PDF).
            frequencyCount = os.path.join(gdb, 'frequencyCount_for_' + str(k)) + "_L" + str(linkNumber)
            frequencyAnalysis(stop_times79_for_, frequencyCount, ["stop_id"])
            arcpy.DeleteField_management(tripsTable, "route_type")
            arcpy.DeleteField_management(stop_time_79, "route_type")
            print(str(linkNumber) + "-----" + "Frequency has been calculated for MODE " + str(k))

            # Join the contents of the FrequencyCount Table to the stops.shp based on the common attribute field stop_id
            joinField(stopsfeature, 'stop_id', frequencyCount, 'stop_id', ['FREQUENCY'])
            arcpy.FeatureClassToFeatureClass_conversion(stopsfeature, output_dir,
                                                        "stops79_84mode" + str(k) + "_L" + str(linkNumber) + ".shp",
                                                        "\"FREQUENCY\" <>0 OR \"FREQUENCY\" IS NOT NULL")
            arcpy.DeleteField_management(stopsfeature, 'FREQUENCY')
            stops79_84 = os.path.join(output_dir, "stops79_84mode" + str(k) + "_L" + str(linkNumber) + ".shp")
            if "stop_code" in stops79_84:
                arcpy.DeleteIdentical_management(stops79_84, ["stop_code"])
            print(str(linkNumber) + "-----" + stops79_84 + " has been created")
            #Append shape files into different lists for specific modes
            if k == 0:
                mode0.append(stops79_84)
            if k == 1:
                mode1.append(stops79_84)
            if k == 2:
                mode2.append(stops79_84)
            if k == 3:
                mode3.append(stops79_84)
            if k== 4:
                mode4.append(stops79_84)
            k = k + 1
        linkNumber=linkNumber+1



    except arcpy.ExecuteError:
        print ("ERROR MSG: Check the link: "+str(linksToDownload[linkNumber]))
        print(arcpy.GetMessages(2))
        print(arcpy.GetMessages(1))
        linkNumber = linkNumber + 1
        continue


### STEP 6 (CHECK THE FLOWCHART IN THE PDF).
#Merge shape files of a specific mode into a new one
print("Merge shape files of a specific mode into a new one")
modes=[mode0,mode1,mode2,mode3,mode4]
allstopsList=[]
modeNumber=0
for m in modes:
    stops_m_=arcpy.Merge_management (m, os.path.join(gdb,"stops_m"+str(modeNumber)))
    #arcpy.DeleteField_management(stops_m_,"wheelchair;stop_timez;stop_url;parent_sta;stop_desc;location_t;stop_id;zone_id;OID_;STOP_ID_1")
    arcpy.DefineProjection_management(stops_m_, output_coords)
    # Project to Equidistant Conic Projection
    stops79 = os.path.join(gdb,'stops79_EqD_'+str(modeNumber))
    arcpy.Project_management(stops_m_, stops79, EqD_CS, "WGS_1984_(ITRF00)_To_NAD_1983", '', "NO_PRESERVE_SHAPE", "",
                             "NO_VERTICAL")
    print('Frequency data has been added to the '+stops79+str(modeNumber))
    modeNumber = modeNumber + 1
    allstopsList.append(stops79)
print(allstopsList)





### Calculating population densities ratio

###STEP 7 (CHECK THE FLOWCHART IN THE PDF).
print('3. Creating buffers and calculation population densities')
# Create 800m buffers(for rail stations) and 400m buffers (for other stops/stations).
allbuffersList=[]
rail=[allstopsList[2]]
buff800=0
for mode800 in rail:
    stopsBuffer = os.path.join(gdb,"buff800_" + str(buff800))
    bufferAnalysis(mode800, stopsBuffer, "800 Meters")
    allbuffersList.append(stopsBuffer)
    buff800=buff800+1
print('800m buffers has been created')
other=[allstopsList[0],allstopsList[1],allstopsList[3],allstopsList[4]]
buff400=0
for mode400 in other:
    stopsBuffer = os.path.join(gdb,"buff400_" + str(buff400))
    bufferAnalysis(mode400, stopsBuffer, "400 Meters")
    allbuffersList.append(stopsBuffer)
    buff400=buff400+1
print('400m buffers has been created')
print(allbuffersList)
#Merge all the buffers and dissolve.
allBuffers=arcpy.Merge_management(allbuffersList, os.path.join(gdb,"allBuffers"), "Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#,buff400_0,Shape_Length,-1,-1,buff400_1,Shape_Length,-1,-1,buff800_0,Shape_Length,-1,-1,buff800_1,Shape_Length,-1,-1;Shape_Area \"Shape_Area\" false true true 8 Double 0 0 ,First,#,buff400_0,Shape_Area,-1,-1,buff400_1,Shape_Area,-1,-1,buff800_0,Shape_Area,-1,-1,buff800_1,Shape_Area,-1,-1")
buffers=arcpy.Dissolve_management (allBuffers, os.path.join(gdb,"buffers"))
print("All buffers have been merged")

### STEP 8 (CHECK THE FLOWCHART IN THE PDF).
#Intersect Buffers and DA
intersectBufDA=arcpy.Intersect_analysis([buffers,da],os.path.join(gdb,"intersectBufDa"), "ALL", "", "INPUT")
### STEP 9 (CHECK THE FLOWCHART IN THE PDF).
intersectCTbufDA=arcpy.Intersect_analysis([intersectBufDA,CT],os.path.join(gdb,"intCTbufDA"), "ALL", "", "INPUT")
#arcpy.DeleteField_management(intersectCTbufDA, "FID_inters;FID_stopsB;Id;FID_DAforS;CSDUID;CCSUID;CDUID;ERUID;PRUID;CMAUID;FID_CTforS;PRUID_1;PRNAME;CMAUID_1;CMAPUID;CMATYPE;OID_;COL0;COL1;COL2")
arcpy.AddField_management(intersectCTbufDA, "areaBUFF", "DOUBLE", "10", "4", "", "", "NULLABLE", "NON_REQUIRED", "")
exp = "!SHAPE.AREA@SQUAREKILOMETERS!"
arcpy.CalculateField_management(intersectCTbufDA, "areaBUFF", exp, "PYTHON_9.3")
arcpy.AddField_management(intersectCTbufDA, "popBUFF", "DOUBLE", "10", "4", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.CalculateField_management(intersectCTbufDA, "popBUFF", "[areaBUFF]*[DA_PopD]", "VB", "")                              ###CHECK FIELD NAME!!!

### STEP 10 (CHECK THE FLOWCHART IN THE PDF).
#Calculate the total population and areas for each census tract(using DA population data)
spatialJoinSUM(CT,intersectCTbufDA,os.path.join(gdb,"PDratioCT"),["areaBUFF","popBUFF"])

### STEP 11 (CHECK THE FLOWCHART IN THE PDF).
#Calculate the ratio between buffers and CTs population densities
arcpy.AddField_management(PDratioCT, PDratioFieldName, "DOUBLE", "10", "4", "", "", "NULLABLE", "NON_REQUIRED", "")
cursor = arcpy.UpdateCursor(PDratioCT)
for row in cursor:
    field0 = row.getValue("sum0")
    field1=row.getValue("sum1")
    field2 = row.getValue('PopD_CT')
    if (field0 == " ") or (field0 == 0) or (field0 == None) or (field2 == " ") or (field2 == 0) or (field2 == None):
            row.setValue(PDratioFieldName, 0)
            cursor.updateRow(row)
    else:
        row.setValue(PDratioFieldName, field1/field0/field2)
        cursor.updateRow(row)
print('Population density ratios have been calculated = "PDratio"')


### STEP 12 (CHECK THE FLOWCHART IN THE PDF).
#Find the dictance from points of interest (origins) to their closest stops/stations using OD Matrix Analysis
print('4. Running OD Matrix Analysis')
#Check Network Analysis extension
if arcpy.CheckExtension("network") == "Available":
    arcpy.CheckOutExtension("network")
else:
    raise arcpy.ExecuteError("Network Analyst Extension license is not available.")
od=0
for destinations in allstopsList:
    try:
        outlayer800 = "outlayer800_" + str(od)
        output_layer_file = os.path.join(output_dir, outlayer800 + ".lyrx")
        # Create a new OD Cost matrix layer. * Maximum walking distance to a bus stop is 800m.
        result_object = arcpy.MakeODCostMatrixLayer_na(network, outlayer800, "Length", "800", 1)
        # Get the layer object from the result object.
        outlayer800 = result_object.getOutput(0)
        arcpy.AddLocations_na(outlayer800, "origins", origins, "", '800 Meters')
        arcpy.AddLocations_na(outlayer800, "destinations", destinations, "", "800 Meters")
        # Solve the OD cost matrix layer
        arcpy.Solve_na(outlayer800)
        print('ODMatrix is solved for mode' + str(od))
        arcpy.SaveToLayerFile_management(outlayer800, output_layer_file, "RELATIVE")
        # Extract OD Lines layer
        linesSublayer = arcpy.mapping.ListLayers(outlayer800, "Lines")[0]
        arcpy.CopyFeatures_management(linesSublayer, os.path.join(gdb, 'odLines_' + str(od)))
        odLines = os.path.join(gdb, 'odLines_' + str(od))
        ### STEP 13 (CHECK THE FLOWCHART IN THE PDF).
        #Calculate Walking Time
        arcpy.AddField_management(odLines, 'WalkingT', "DOUBLE", 10)
        arcpy.CalculateField_management(odLines, "WalkingT", '!Total_Length!/80', "PYTHON")
        print("Walking time (for odLines) has been calculated.....MODE - " + str(od))
        # Spatial Join: Lines+stops79
        linesWalkWait = os.path.join(gdb, 'linesWalkWait_' + str(od))
        arcpy.SpatialJoin_analysis(odLines, destinations, linesWalkWait, "JOIN_ONE_TO_MANY", "KEEP_ALL", '',
                                   "INTERSECT",
                                   "", "")
        # Spatial Join: POI+linesWalkWait
        poiWalkWait = os.path.join(gdb, 'poiWalkWait_' + str(od))
        arcpy.SpatialJoin_analysis(origins, linesWalkWait,
                                   poiWalkWait, "JOIN_ONE_TO_MANY",
                                   "KEEP_ALL", '', "INTERSECT", "", "")
        ### STEP 14 (CHECK THE FLOWCHART IN THE PDF).
        #Calculate Equivalent Frequency
        arcpy.AddField_management(poiWalkWait, 'EF' + str(od), "DOUBLE", "10", "4", "", "", "NULLABLE", "NON_REQUIRED",
                                  "")
        arcpy.CalculateField_management(poiWalkWait, 'EF' + str(od), "30/([WalkingT]+0.5*(120/[FREQUENCY]))", "VB", "")
        print('Equivalent Frequencies for each POI have been calculated....MODE' + str(od))
        joinField(origins, pccfIDfield, poiWalkWait, pccfIDfield, 'EF' + str(od))
        print("EF is in pccf-table----" + str(od))
        od = od + 1
    except arcpy.ExecuteError:
        print(arcpy.GetMessages(2))
        print(arcpy.GetMessages(1))
        arcpy.AddField_management(origins, 'EF' + str(od), "DOUBLE", 10)
        arcpy.CalculateField_management(origins, 'EF' + str(od), '0', "PYTHON")
        od = od + 1

### STEP 15 (CHECK THE FLOWCHART IN THE PDF).
#Transfer EF values to CTs using SUM-merge rule
print ('5.  Calculating PTAI for CT...')
spatialJoinCTsum(PDratioCT,origins, PTAI_CT)

### STEP 16 (CHECK THE FLOWCHART IN THE PDF).
#Calculate WEF
arcpy.AddField_management(PTAI_CT, 'WEF', "DOUBLE", "10", "4", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.CalculateField_management(PTAI_CT, 'WEF', "[EFsum_2]+([EFsum_0]+[EFsum_1]+[EFsum_3]+[EFsum_4])/2", "VB", "")
print("WEF has been calculated for CT")
#Calculate PTAI
calculatePTAI(PTAI_CT)

### STEP 17 (CHECK THE FLOWCHART IN THE PDF).
#Transfer EF values to DAs using SUM-merge rule
print ('6.  Calculating PTAI for DA...')
spatialJoinCTsum(da,origins, PTAI_DA)

### STEP 18 (CHECK THE FLOWCHART IN THE PDF).
#Calculate WEF represents PTAI in our case
arcpy.AddField_management(PTAI_DA, 'WEF', "DOUBLE", "10", "4", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.CalculateField_management(PTAI_DA, 'WEF', "[EFsum_2]+([EFsum_0]+[EFsum_1]+[EFsum_3]+[EFsum_4])/2", "VB", "")
print("WEF (=PTAI) has been calculated for DA")

print ('Done!!!')


deleteFields=["Join_Count","TARGET_FID","FID_intersectBufDa","FID_buffers","DAUID","geo_code","DA_PopD","DAarea","DA_Pop","sum0","sum1","a0","a1","a2","a3","a4","a5","a6","a7","a8","EFsum_CT0","EFsum_CT1","EFsum_CT2","EFsum_CT3","EFsum_CT4","Shape_Length","Shape_Area"]
if deleteFields in PTAI_CT:
    for fieldToDelete in deleteFields:
        arcpy.DeleteField_management(PTAI_CT,fieldToDelete)