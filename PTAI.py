# Developed by Wei Liu (weil [AT] mun [DOT] ca | www.cs.mun.ca/~weil)& Yulmetova Maria
# Version: Aug 14, 2019
# Built Environment and Active Populations Lab
# Memorial University of Newfoundland


##This is a generalized script can be used for all the cities,
##but before running the script, it is important to make sure the
##input file names are consistent. For example, "DA_Halifax_EqD.shp",
##"CT_Halifax_EqD.shp", "PCCF_Halifax_EqD.shp", "Roads_Halifax_EqD_ND.nd"
##are input file names for Halifax, if you want to run the code on other cities
##make sure you replace "Halifax" to the other city name


import urllib2                         #This is a extensible library for opening URLs
import zipfile                         #This module provides tools to create, read, write, append, and list a ZIP file
import arcpy                           #This package provides a useful and productive way to perform geographic data analysis, data conversion, data management, and map automation with Python.
import os                              #Provides os.path.join 
import csv                             #This package provides tool to open and read csv files
import sys
arcpy.CheckOutExtension("3D")
import shutil


#Define a function to convert txt-files (stop_times.txt, trips.txt and routes.txt) to GDB tables
#Only select data that within the peak hour (7 - 9 am)
def getGDBtable(txtFileName, gdbTableName):                             #Get GDBtable from txt-file (stop_times, trips and routes)
    print("Creating a new gdb-table for "+str(txtFileName))
    ispy3 = sys.version_info >= (3, 0)
    if ispy3:
        f = open(txtFileName, encoding="utf-8-sig")
    else:
        f = open(txtFileName)
    reader = csv.reader(f)
    # Put everything in utf-8 to handle BOMs and weird characters.
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
        stop_time_79=arcpy.TableToTable_conversion(gdbTable, gdb, "stoptime79",
                                                 "(\"arrival_ti\" >='07:00:00' AND \"arrival_ti\" <='09:00:00')OR (\"arrival_ti\" >='7:00:00' AND \"arrival_ti\" <='9:00:00')OR (\"arrival_ti\" >=' 7:00:00' AND \"arrival_ti\" <=' 9:00:00')")
        arcpy.DeleteField_management(stop_time_79, "departure_;stop_seque;stop_heads;pickup_typ;drop_off_t;shape_dist")
        print("A new table of all stop times from 7 am to 9 am has been created.")
    if route_type in fields:                                            #For routes table: created several tables for each mode


        route_type0 = arcpy.TableToTable_conversion(gdbTable, gdb, "route_type0", "route_type = '0'")     #0 - Tram, Streetcar, Light rail.     
        route_type1 = arcpy.TableToTable_conversion(gdbTable, gdb, "route_type1", "route_type = '1'")     #1 - Subway, Metro.     
        route_type2 = arcpy.TableToTable_conversion(gdbTable, gdb, "route_type2", "route_type = '2'")     #2 - Rail.     
        route_type3 = arcpy.TableToTable_conversion(gdbTable, gdb, "route_type3", "route_type = '3'")     #3 - Bus.
        listTypes=[route_type0,route_type1,route_type2,route_type3]
        for route_type in listTypes:
            arcpy.DeleteField_management(route_type,"agency_id;route_shor;route_long;route_desc;route_url;route_colo;route_text")
    if field_trip_headsign in fields:
        arcpy.DeleteField_management(gdbTable, "trip_heads;service_id;trip_short;direction_;block_id;wheelchair")
        print("TripsTable has been created")

    else:
        print("no selection")


def txtToPoints(txtfile,featureName):
    max_stop_desc_length = 250
    print("2. Reading input stops.txt file...")
    f = open(txtfile)
    reader = csv.reader(f)
    # First row is column names:
    columns = [name.strip('\xef\xbb\xbf') for name in next(reader)]
    #columns = [name.strip() for name in next(reader)]
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
    # Find incides of stop_lat and stop_lon columns
    stop_lat_idx = columns.index("stop_lat")
    stop_lon_idx = columns.index("stop_lon")
    stop_id_idx = columns.index("stop_id")
    # Truncate the long field names up to 10 characters.
    columns = [c[0:10] for c in columns]
    # Create new feature class and add the right fields; Hard-wire all the columns to be text values
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
                # Get the lat/lon values. If float covnersion fails, there is a problem
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
                # GTFS stop lat/lon is written in WGS1984
                ptGeometry = arcpy.PointGeometry(pt, WGSCoords)
                if output_coords != WGSCoords:
                    ptGeometry = ptGeometry.projectAs(output_coords) 

                cur.insertRow((ptGeometry,) + tuple(row))

        print("Stops.shp has been created.")

    except Exception as err:
        arcpy.AddError("Error writing stops.txt data to feature class.")
        raise

# Define a function to join field and print a message when finished
def joinField(in_data,in_field,join_table,join_field,fieldName):
    arcpy.JoinField_management (in_data, in_field, join_table, join_field,fieldName)
    print("The "+str(fieldName)+" has been added to the "+str(in_data))

# Define a function to convert tables
def tableToTable(in_rows,tableName,where_clause):
    arcpy.TableToTable_conversion(in_rows, gdb, tableName,where_clause)

# Define a function to conduct Frequency Analysis and print a message when finished
def frequencyAnalysis (in_table, out_table, frequency_fields):
    arcpy.Frequency_analysis(in_table, out_table,frequency_fields)
    print("Frequency analysis has been completed.")

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
        # First get the EF fieldmap. EF is a field in the cities feature class.
        # The output will have the DAs with the attributes of the PointWalkWait.
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


    # Run the Spatial Join tool, using the defaults for the join operation and join type
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
    
    fields = arcpy.ListFields(joinFeatures)
    fieldsName = []
    for field in fields:
        fieldsName.append(field.name)
    efcount = 0
    for efcount in range(4):
        if ('EF'+str(efcount)) in fieldsName:
            EF = fieldmappings.findFieldMapIndex('EF'+str(efcount))
            fieldmap = fieldmappings.getFieldMap(EF)
            # Get the output field's properties as a field object
            field = fieldmap.outputField

            # Rename the field and pass the updated field object back into the field map
            field.name = "EFsum_CT"+str(efcount)
            field.aliasName = "EFsum_CT"+str(efcount)
            fieldmap.outputField = field

            # Set the merge rule to mean
            fieldmap.mergeRule = "Sum"
            fieldmappings.replaceFieldMap(EF, fieldmap)
    arcpy.SpatialJoin_analysis(targetFeatures, joinFeatures, output, "#", "#", fieldmappings)        

      

#Variables:
path1 = "./intermediate"
if os.path.exists(path1):
    shutil.rmtree(path1)
os.mkdir(path1)
inter_dir = path1

path2 = "./output"
if os.path.exists(path2):
    shutil.rmtree(path2)
os.mkdir(path2)
output_dir = path2

input_dir="./input"

da=os.path.join(input_dir,"DA_Oakville_EqD.shp")
CT=os.path.join(input_dir,"CT_Oakville_EqD.shp")

WGSCoords = "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984', \
    SPHEROID['WGS_1984',6378137.0,298.257223563]], \
    PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]; \
    -400 -400 1000000000;-100000 10000;-100000 10000; \
    8.98315284119522E-09;0.001;0.001;IsHighPrecision"
output_coords = WGSCoords
EqD_CS="PROJCS['North_America_Equidistant_Conic',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Equidistant_Conic'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-96.0],PARAMETER['Standard_Parallel_1',20.0],PARAMETER['Standard_Parallel_2',60.0],PARAMETER['Latitude_Of_Origin',40.0],UNIT['Meter',1.0]]"



stop_times = os.path.join(inter_dir, 'stop_times.txt')
trips = os.path.join(inter_dir, "trips.txt")
routes = os.path.join(inter_dir, "routes.txt")
stops = os.path.join(inter_dir,'stops.txt')


origins = os.path.join(input_dir,'PCCF_Oakville_EqD.shp')

network = os.path.join(input_dir,'Roads_Oakville_EqD_ND.nd')


gdb = arcpy.CreateFileGDB_management(inter_dir, "gtfs.gdb")
gdb = os.path.join(inter_dir,'gtfs.gdb')

stops_timeTableName = 'stops_timeTable' 
tripsTableName = "tripsTable" 
routesTableName = "routesTable" 
stopsfeatureName = 'stops'


PTAI_CT = os.path.join(gdb,"PTAI_CT_")
PTAI_DA = os.path.join(gdb,"PTAI_DA")
PDratioCT = os.path.join(gdb,"PDratioCT")

PDratioFieldName="PDratio"
pccfIDfield="pccfID"

# 4 modes
mode0 = []
mode1 = []
mode2 = []
mode3 = []

with zipfile.ZipFile("gtfs.zip", "r") as zip_ref:
    zip_ref.extractall(inter_dir)

getGDBtable(stop_times, stops_timeTableName)
getGDBtable(trips, tripsTableName)
getGDBtable(routes, routesTableName)

txtToPoints(stops, stopsfeatureName)

tripsTable = os.path.join(gdb, tripsTableName)
stop_time_79 = os.path.join(gdb, "stoptime79")

# 4 modes
route_type_0 = os.path.join(gdb, "route_type0")
route_type_1 = os.path.join(gdb, "route_type1")
route_type_2 = os.path.join(gdb, "route_type2")
route_type_3 = os.path.join(gdb, "route_type3")
route_type_list = [route_type_0, route_type_1, route_type_2, route_type_3]

stopsfeature = os.path.join(gdb, stopsfeatureName)


k = 0
for mode in route_type_list:
    joinField(tripsTable, 'route_id', mode, 'route_id', "route_type")
    joinField(stop_time_79, "trip_id", tripsTable, "trip_id", "route_type")
    stop_times79_for_Name = "stop_times79_for_" + str(k)
    tableToTable(stop_time_79, stop_times79_for_Name, "\"route_type\" IS NOT NULL")
    stop_times79_for_ = os.path.join(gdb, stop_times79_for_Name)
    frequencyCount = os.path.join(gdb, 'frequencyCount_for_' + str(k))
    frequencyAnalysis(stop_times79_for_, frequencyCount, ["stop_id"])
    arcpy.DeleteField_management(tripsTable, "route_type")
    arcpy.DeleteField_management(stop_time_79, "route_type")
    print("-----" + "Frequency has been calculated for MODE " + str(k))

    # Join the contents of the FrequencyCount Table to the stops.shp based on the common attribute field stop_id
    joinField(stopsfeature, 'stop_id', frequencyCount, 'stop_id', ['FREQUENCY'])
    arcpy.FeatureClassToFeatureClass_conversion(stopsfeature, inter_dir,
                                                "stops79_84mode" + str(k) + ".shp",
                                                "\"FREQUENCY\" <>0 OR \"FREQUENCY\" IS NOT NULL")
    arcpy.DeleteField_management(stopsfeature, 'FREQUENCY')
    stops79_84 = os.path.join(inter_dir, "stops79_84mode" + str(k) + ".shp")
    arcpy.DeleteIdentical_management(stops79_84, ["stop_code"])
    print("-----" + stops79_84 + "has been created")

    if k == 0:
        mode0.append(stops79_84)
    if k == 1:
        mode1.append(stops79_84)
    if k == 2:
        mode2.append(stops79_84)
    if k == 3:
        mode3.append(stops79_84)
    print(mode0)
    print(mode1)
    print(mode2)
    print(mode3)
    k = k + 1


modes=[mode0,mode1,mode2,mode3]


allstopsList=[]
modeNumber=0
for m in modes:
    stops_m_=arcpy.Merge_management (m, os.path.join(gdb,"stops_m"+str(modeNumber)))
    arcpy.DeleteField_management(stops_m_,
                                 "wheelchair;stop_timez;stop_url;parent_sta;stop_desc;location_t;stop_id;zone_id;OID_;STOP_ID_1")

    arcpy.DefineProjection_management(stops_m_, output_coords)
    # Project to Equidistant Conic Projection
    stops79 = os.path.join(gdb,'stops79_EqD_'+str(modeNumber))
    arcpy.Project_management(stops_m_, stops79, EqD_CS, "WGS_1984_(ITRF00)_To_NAD_1983", '', "NO_PRESERVE_SHAPE", "",
                             "NO_VERTICAL")

    print('Frequency data has been added to the '+stops79+str(modeNumber))
    modeNumber = modeNumber + 1

    allstopsList.append(stops79)
print(allstopsList)


# Calculating population densities ratio
print('3. Creating buffers and calculation population densities')
    # Create buffers and dissolve
allbuffersList=[]
subway_rail=[allstopsList[1],allstopsList[2]]
bus_tram=[allstopsList[0],allstopsList[3]]
buff400=0
for mode400 in bus_tram:
    stopsBuffer = os.path.join(gdb,"buff400_" + str(buff400))
    bufferAnalysis(mode400, stopsBuffer, "400 Meters")
    allbuffersList.append(stopsBuffer)
    buff400=buff400+1

print('400m buffers has been created')
print(allbuffersList)

buff800=0
for mode800 in subway_rail:
    stopsBuffer = os.path.join(gdb,"buff800_" + str(buff800))
    bufferAnalysis(mode800, stopsBuffer, "800 Meters")
    allbuffersList.append(stopsBuffer)
    buff800=buff800+1
print('800m buffers has been created')
print(allbuffersList)




allBuffers=arcpy.Merge_management(allbuffersList, os.path.join(gdb,"allBuffers"), "Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#,buff400_0,Shape_Length,-1,-1,buff400_1,Shape_Length,-1,-1,buff800_0,Shape_Length,-1,-1,buff800_1,Shape_Length,-1,-1;Shape_Area \"Shape_Area\" false true true 8 Double 0 0 ,First,#,buff400_0,Shape_Area,-1,-1,buff400_1,Shape_Area,-1,-1,buff800_0,Shape_Area,-1,-1,buff800_1,Shape_Area,-1,-1")
buffers=arcpy.Dissolve_management (allBuffers, os.path.join(gdb,"buffers"))
print("All buffers have been merged")




#Intersect Buffers and DA

intersectBufDA=arcpy.Intersect_analysis([buffers,da],os.path.join(gdb,"intersectBufDa"), "ALL", "", "INPUT")
intersectCTbufDA=arcpy.Intersect_analysis([intersectBufDA,CT],os.path.join(gdb,"intCTbufDA"), "ALL", "", "INPUT")
arcpy.DeleteField_management(intersectCTbufDA, "FID_inters;FID_stopsB;Id;FID_DAforS;CSDUID;CCSUID;CDUID;ERUID;PRUID;CMAUID;FID_CTforS;PRUID_1;PRNAME;CMAUID_1;CMAPUID;CMATYPE;OID_;COL0;COL1;COL2")

arcpy.AddField_management(intersectCTbufDA, "areaBUFF", "DOUBLE", "10", "4", "", "", "NULLABLE", "NON_REQUIRED", "")
exp = "!SHAPE.AREA@SQUAREKILOMETERS!"
arcpy.CalculateField_management(intersectCTbufDA, "areaBUFF", exp, "PYTHON_9.3")
arcpy.AddField_management(intersectCTbufDA, "popBUFF", "DOUBLE", "10", "4", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.CalculateField_management(intersectCTbufDA, "popBUFF", "[areaBUFF]*[PopD_DA]", "VB", "")




spatialJoinSUM(CT,intersectCTbufDA,os.path.join(gdb,"PDratioCT"),["areaBUFF","popBUFF"])

#Calculate a ratio BufferPopDensity/CTPopDensity:

arcpy.AddField_management(PDratioCT, PDratioFieldName, "DOUBLE", "10", "4", "", "", "NULLABLE", "NON_REQUIRED", "")
arcpy.CalculateField_management(PDratioCT, PDratioFieldName, "([sum1]/[sum0])/[PopD_CT]", "VB", "")
print('Population density ratios have been calculated = "PDratio"')


#OD Matrix Analysis
print('4. Running OD Matrix Analysis')
#Check Network Analysis extension
if arcpy.CheckExtension("network") == "Available":
    arcpy.CheckOutExtension("network")
else:
    raise arcpy.ExecuteError("Network Analyst Extension license is not available.")

# Set local variables

#destinationsList = [os.path.join(inter_dir,"stops79_EqDmode0.shp"),os.path.join(inter_dir,"stops79_EqDmode1.shp"),os.path.join(inter_dir,"stops79_EqDmode2.shp")]

# Delete Duplicates from PCCF
#arcpy.DeleteIdentical_management(origins, "field6;field7" , "", "0")                                                           

                                                                                                                          
od=0                                                                                                                          
for destinations in allstopsList:
    if arcpy.management.GetCount(destinations)[0] != "0":
        outlayer800 = "outlayer800_" + str(od)
        output_layer_file = os.path.join(inter_dir, outlayer800 + ".lyrx")
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

        ###Calculate Walking Time
        arcpy.AddField_management(odLines, 'WalkingTime', "DOUBLE", 10)
        arcpy.CalculateField_management(odLines, "WalkingTime", '!Total_Length!/80', "PYTHON")
        print("Walking time (for odLines) has been calculated.....MODE - " + str(od))

        # Spatial Join: Lines+stops79
        linesWalkWait = os.path.join(gdb, 'linesWalkWait_' + str(od))
        arcpy.SpatialJoin_analysis(odLines, destinations, linesWalkWait, "JOIN_ONE_TO_MANY", "KEEP_ALL", '', "INTERSECT",
                                   "", "")

        # Spatial Join: POI+linesWalkWait
        poiWalkWait = os.path.join(gdb, 'poiWalkWait_' + str(od))
        arcpy.SpatialJoin_analysis(origins, linesWalkWait,
                                   poiWalkWait, "JOIN_ONE_TO_MANY",
                                   "KEEP_ALL", '', "INTERSECT", "", "")

        #  Calculate Equivalent Frequency
        arcpy.AddField_management(poiWalkWait, 'EF' + str(od), "DOUBLE", "10", "4", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.CalculateField_management(poiWalkWait, 'EF' + str(od), "30/([WalkingTime]+0.5*(120/[FREQUENCY]))", "VB", "")                  
        print('Equivalent Frequencies for each POI have been calculated....MODE' + str(od))
        joinField(origins, pccfIDfield, poiWalkWait, pccfIDfield, 'EF' + str(od))
        print("EF is in pccf-table----" + str(od))     
    od = od + 1



print ('5.  Calculating PTAI for CT...(using EF sum)')


spatialJoinCTsum(PDratioCT,origins, PTAI_CT)
spatialJoinCTsum(da,origins, PTAI_DA)


CTfields = arcpy.ListFields(PTAI_CT)
CTfieldsName = []
for CTfield in CTfields:
    CTfieldsName.append(CTfield.name)
for i in range(4):
    if ('EFsum_CT'+str(i)) not in CTfieldsName:
        arcpy.AddField_management(PTAI_CT, 'EFsum_CT'+str(i), "DOUBLE", "10", "4", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.CalculateField_management(PTAI_CT, 'EFsum_CT'+str(i), 0, "VB", "")

DAfields = arcpy.ListFields(PTAI_DA)
DAfieldsName = []
for DAfield in DAfields:
    DAfieldsName.append(DAfield.name)
for i in range(4):
    if ('EFsum_CT'+str(i)) not in DAfieldsName:
        arcpy.AddField_management(PTAI_DA, 'EFsum_CT'+str(i), "DOUBLE", "10", "4", "", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.CalculateField_management(PTAI_DA, 'EFsum_CT'+str(i), 0, "VB", "")



arcpy.AddField_management(PTAI_CT, 'WEF', "DOUBLE", "10", "4", "", "", "NULLABLE", "NON_REQUIRED", "")
#arcpy.CalculateField_management(PTAI_CT, 'WEF', "[EFsum_2]+([EFsum_0]+[EFsum_1]+[EFsum_3]+[EFsum_4])/2", "VB", "")
arcpy.CalculateField_management(PTAI_CT, 'WEF', "[EFsum_CT2]+([EFsum_CT0]+[EFsum_CT1]+[EFsum_CT3])/1.5", "VB", "")
print("WEF has been calculated for CT")

calculatePTAI(PTAI_CT)

arcpy.AddField_management(PTAI_DA, 'WEF', "DOUBLE", "10", "4", "", "", "NULLABLE", "NON_REQUIRED", "")
#arcpy.CalculateField_management(PTAI_DA, 'WEF', "[EFsum_2]+([EFsum_0]+[EFsum_1]+[EFsum_3]+[EFsum_4])/2", "VB", "")
arcpy.CalculateField_management(PTAI_DA, 'WEF', "[EFsum_CT2]+([EFsum_CT0]+[EFsum_CT1]+[EFsum_CT3])/1.5", "VB", "")
print("WEF has been calculated for DA")


for od in range(4):
    arcpy.DeleteField_management(origins, 'EF' + str(od))

arcpy.FeatureClassToShapefile_conversion([PTAI_CT, PTAI_DA], output_dir)

print ('Done!')

