NOTICE: It&#39;s better to navigate the folders with ArcGIS. Because some data such as shapefile contains .cpg, .dbf, .shp, .xml, .prj and so on but they should be considered as a single dataset.

Directory: Z:\Research\dfuller\Walkabilly\exposure\transit

CT and DA folder contains census tract and dissemination area data of Canada. The topologyCTDA.gdb and TopologyCTDA.mxd are used to check the topology correctness of CT and DA data. There is no topology error in the dataset.

| **PRUID** | **Province or territory name** | **Abbreviation** |
| --- | --- | --- |
| 10 | Newfoundland and Labrador/Terre-Neuve-et-Labrador | NL |
| 11 | Prince Edward Island/Île-du-Prince-Édouard | PE |
| 12 | Nova Scotia/Nouvelle-Écosse | NS |
| 13 | New Brunswick/Nouveau-Brunswick | NB |
| 24 | Quebec/Québec | QC |
| 35 | Ontario | ON |
| 46 | Manitoba | MB |
| 47 | Saskatchewan | SK |
| 48 | Alberta | AB |
| 59 | British Columbia/Colombie-Britannique | BC |
| 60 | Yukon | YK |
| 61 | Northwest Territories/Territoires du Nord-Ouest | NT |
| 62 | Nunavut | NU |

The following provinces or territories do not have Census Tract data: PE, YK, NT, NU

Each province/territory has a folder named as &quot;PTAI\_[Abbreviation]&quot;, for example, for Alberta, the folder is &quot;PTAI\_AB&quot;. Each PTAI folder has the same structure. Inside the PTAI folder, there is a folder called &quot;input&quot;, it contains all the input data for the python script. These input data are intermediate data generated from &quot;CT and DA&quot; data and the census data downloaded from Statistics Canada.

Inside the &quot;input&quot; folder, there is a file geodatabase named with the abbreviation of the province/territory. For example, the geodatabase for Alberta is named &quot;AB.gdb&quot;. The geodatabase contains both CT and DA data with NAD 83 North\_America\_Equidistant\_Conic projected coordinate system and NAD 83 North\_America\_Albers\_Equal\_Area\_Conic projected coordinate system. The data with equal area projection is used to calculate the area of CT and DA.

Data preprocessing steps:

1. Change the projection of CT and DA data from Lambert\_Conformal\_Conic to North\_America\_Albers\_Equal\_Area\_Conic

Input:

lct\_000a16a\_e.shp

Output (feature classes in geodatabase):

CT\_CA\_EqA (North\_America\_Albers\_Equal\_Area\_Conic)

 Method:

  Project (Data Management)

1. Create CT data for each province/territory

Input:

CT\_CA\_EqA

Output (feature classes in geodatabase):

CT\_AB\_EqA, CT\_BC\_EqA, CT\_MB\_EqA…and so on

Method:

1. Open attribute table, select by attributes
2. Click &quot;PRUID&quot;, click &quot;Get Unique Values&quot;
3. Type an SQL query &quot;PRUID = 48&quot; (here 48 represents AB, the PRUID corresponding province can be found above), click apply
4. Right click the layer and click &quot;Data -\&gt; Export Data&quot;, then save the selected data as a new future class in the geodatabase
5. Repeat the steps for other provinces/territories

1. Create DA data for each province/territory

Similar to CT

Input:

DA\_CA\_EqA

Output (feature classes in geodatabase):

DA\_AB\_EqA, DA\_BC\_EqA, DA\_MB\_EqA…and so on

Method:

1. Open attribute table, select by attributes
2. Click &quot;PRUID&quot;, click &quot;Get Unique Values&quot;
3. Type an SQL query &quot;PRUID = 48&quot; (here 48 represents AB, the PRUID corresponding province can be found above), click apply
4. Right click the layer and click &quot;Data -\&gt; Export Data&quot;, then save the selected data as a new future class in the geodatabase
5. Repeat the steps for other provinces/territories

1. Create population data table for each province/territory

Input:

PopulationCanada.csv

Output:

 Population\_AB.xlsx

 Population\_AB (standalone table in geodatabase)

Method:

1. Select all the records and click &quot;Format As Table&quot;
2. In &quot;PRUID&quot; column, select &quot;PRUID = 48&quot; (here 48 represents AB province, the PRUID corresponding province can be found above)
3. Copy the data and paste it to Population\_AB.xlsx file
4. In ArcMap, use &quot;Excel to Table&quot; to create a standalone table &quot;Population\_AB&quot; in the geodatabase
5. Repeat the steps for other provinces/territories

1. Table join between DA data and population data

Input:

DA\_AB\_EqA

 Population\_AB

Output:

 DA\_AB\_EqA (with population information in the attribute table)

Method:

1. Notice that the &quot;geographic code&quot; in the table is &quot;DAUID&quot; in the DA layer, but their data types are different, so add a new field &quot;DAUID&quot; in the population data table
2. Calculate the value of &quot;DAUID&quot; using &quot;Field Calculator&quot;, type &quot;DAUID = Geographic\_code&quot;
3. Right click the layer select &quot;Joins and Relates-\&gt; Join&quot;
4. Select &quot;Join attributes from a table&quot;, then choose the field in this layer that the join will based on &quot;DAUID&quot;, choose the &quot;DAUID&quot; field in &quot;Population\_AB&quot; table.
5. Repeat the steps for other provinces/territories

1. Create a summary table to calculate the population in each CT

Input:

 DA\_AB\_EqA (with population information in the attribute table)

Output:

 Population\_AB\_CT (Standalone table in geodatabase)

Method:

1. Open the attribute table of DA\_AB\_EqA
2. Highlight &quot;CTUID&quot; field, click &quot;Summarize…&quot; (NOTICE, this step cannot use &quot;CTNAME&quot;!!!)
3. Choose &quot;Population\_NL.Population\_2016&quot; -\&gt; &quot;Sum&quot; to be included in the output table
4. The output table contains the population information for each CT
5. Repeat the steps for other provinces/territories

1. Table join between CT\_AB\_EqA and Population\_AB\_CT

Input:

 CT\_AB\_EqA

Population\_AB\_CT

Output:

 CT\_AB\_EqA (with population information in the attribute table)

Method:

1. Right click the layer select &quot;Joins and Relates-\&gt; Join&quot;
2. Select &quot;Join attributes from a table&quot;, then choose the field in this layer that the join will based on &quot;CTNAME&quot;, choose the &quot;CTNAME&quot; field in &quot;Population\_AB\_CT&quot; table.
3. Repeat the steps for other provinces/territories

1. Calculate the population density for CT

Input:

 CT\_AB\_EqA (with total population for each CT)

Output:

CT\_AB\_EqA (with population density for each CT)

Method:

1. Open attribute table of CT\_AB\_EqA, in &quot;Table Options&quot;, select &quot;Add Field…&quot;
2. Add two fields, one of them is &quot;Area\_in\_km2&quot;, another is &quot;PopD\_CT&quot;, both of their types are &quot;double&quot;
3. For the &quot;Area\_in\_km2&quot;, use &quot;Calculate Geometry…&quot; to calculate the area, units in square kilometers.
4. For PopD\_CT, use &quot;Field Caculator…&quot;. The formula is &quot;PopD\_CT = Sum\_population\_2016/Area\_in\_km2&quot;
5. Repeat the steps for other provinces/territories

1. Change the projection of CT and DA data from North\_America\_Albers\_Equal\_Area\_Conic to North\_America\_Equidistant\_Conic

Input:

CT\_CA\_EqA (North\_America\_Albers\_Equal\_Area\_Conic)

Output (feature classes in geodatabase):

CT\_CA\_EqD (North\_America\_Equidistant\_Conic)

 Method:

  Project (Data Management)

1. Create PCCF point feature

Input:

pccfNat\_fccpNat\_062017.txt

Output:

PCCF point feature for each province

 Method:

1. Since the .txt file has too many records to convert to .csv file directly, an R script is used to divide the .txt file based on the first letter of the post code. The outputs are PCCF\_AB.txt, PCCF\_BC.txt and so on.
2. Open Excel, export the PCCF\_AB.txt to .csv file. &quot;Data&quot; -\&gt; &quot;Get Data From Text&quot;, create break lines to separate each field. Save file as PCCF\_AB.csv
3. In ArcMap, &quot;File&quot; -\&gt; &quot;Add Data&quot; -\&gt; &quot;Add XY Data&quot;. Choose PCCF\_AB.csv, set longitude value as X field, latitude value as Y field, and coordinate system as &quot;WGS 84&quot;.
4. Use &quot;Project&quot; management tool to project the point feature to North\_America\_Equidistant\_Conic coordinate system. The outputs for this step are PCCF\_AB\_EqD and so on

1. Create CT and DA data for cities

Input:

 CT and DA data for provinces (for example: CT\_AB\_EqD)

Output:

CT and DA data for provinces (for example: CT\_Calgary\_EqD.shp)

Method:

 Select by attribute (CMANAME = &quot;Calgary&quot;), then export the selected data

1. Clip PCCF data to city boundaries

Input:

 PCCF data for provinces

Output:

 PCCF data for cities

Method:

 Use &quot;Clip&quot; tool, choose PCCF\_AB\_EqD as Input Features, CT\_Calgary\_EqD as Clip Features. After creating the PCCF data for cities, one more step is to create a &quot;pccfID&quot; field for it. In the attribute table, &quot;Add Field&quot;, then &quot;Field Calculator…&quot;, &quot;pccfID = FID&quot;

1. Create road network dataset for cities

Input:

 CanVec Data of Canada (for example: canvec\_50K\_AB\_Transport\_shp/canvec\_50K\_AB\_Transport/road\_segment\_1\_1.shp)

Output:

 Roads network dataset for cities

Method:

1. Project the input data to North\_America\_Equidistant\_Conic coordinate system
2. Clip the roads segment data using CT for cities boundaries, get roads line feature for cities
3. In Catalog, right click the roads line feature, click &quot;New Network Dataset&quot;, and notice that the network dataset can be only created based on shapefile.

1. Now the input data for the script are ready and it is inside the &quot;input&quot; folder of each city folder. The input data is: CT, DA, PCCF and Roads network. All of them have the same coordinate system -- North\_America\_Equidistant\_Conic.

An example is:

CT\_Calgary\_EqD.shp

DA\_Calgary\_EqD.shp

PCCF\_Calgary\_EqD.shp

Roads\_Calgary\_EqD.shp

Roads\_Calgary\_EqD\_ND.nd

Roads\_Calgary\_EqD\_ND\_Junctions.shp

1. Download the transit feed (GTFS) data for each city
2. Run the script. After running the script, an intermediate folder is created, and all the intermediate data is inside the folder. The PTAI for CT and DA are created
3. Copy the PTAI for CT and DA from the geodatabase to shapefiles in a new &quot;output&quot; folder.
4. Create map for each city with CT and DA level.

Trouble Shooting:

1. The script for each city are slightly different in terms of the input name. Before running the script, make sure replace the old city name with the new city name. There are 4 file names need to be replaced.
2. In ArcGIS, when a process accesses a dataset, it locks the dataset, preventing other processes from changing it. Therefore, when run the script, it is important to close all the related dataset in ArcGIS, or even close ArcGIS itself. Due to the same reason, sometimes a folder/gdb/file cannot be deleted. In case of this, ArcGIS needs to be closed.
3. If we add a field to a table, but the field already exists, there will be error. Thus if we run the script more than one time, it is important to make sure the original input files are not changed. Specifically, check whether the &quot;EF&quot; filed has been deleted from PCCF data table.
4. Gtfs data needs to be checked, for example the format of gtfs data of red deer is not suitable for the script, so I downloaded another dataset.
5. Previously, the output of Regina area has too many 0s. That&#39;s because in the script, several fields have been deleted thus when run the join management, the output of point feature only contains 1 point
6. When run the OD Matrix Analysis, if the mode is empty, there will be an error. For example, Calgary, Edmonton and Waterloo routes only have mode 0 (Tram, Streetcar, Light rail) and mode 3 (bus). So we need to skip the mode 1 and mode 2 when running the OD Matrix Analysis.
7. For the map document files (.mxd), it&#39;s better to store the relative pathnames. In ArcGIS, &quot;File&quot; -\&gt; &quot;Map Document Properties&quot; -\&gt; &quot;Pathnames&quot;, check &quot;Store relative pathnames to data sources&quot;. Thus when the map document file moves together with the source files (PTAI for DA and CT), the link won&#39;t be broken. In case the link is broken, that means the document cannot find the source file, then we have to click the layer properties, find &quot;source&quot; tab and set data source.
