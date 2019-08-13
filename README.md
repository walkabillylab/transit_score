
# Public Transport Accessibility Index

Development of Transit Score measure for CANUE - Canadian Urban Environmental Health Research Consortium. 

## Authors

* [Wei Liu](https://www.cs.mun.ca/~weil/)
* Yulmetova Maria

## Introduction
The Public Transport Accessibility Index (PTAI) was calculated based on the method described by Saghapour, 2016[1] to measure the access level to public transport for each census tract in different metropolitan areas of Canada. 
This approach consists of two main procedures. The first of them relates to the distances from points of interest and their closest stops/stations. The second one includes walking catchments and CTs population densities proportions calculations. The PTAI was calculated for each census tract.
In addition, the access level was calculated for each DA. In this case, the proportions between population densities in different geographic levels were not considered.
A flow chart is attached to visualize the algorithm.


## Input Data 
The input data for calculating the PTAI are as follows:
### 1. Geographic data at Census Tract (CT) level
This is a shapefile contains geographic features at CT level in cencus year 2016. CT are small, relatively stable geographic areas that have a population of less than 10, 000. It's downloaded from Statistics Canada. 
### 2. Geographic data at Dissemination Area (DA) level
This is a shapefile contains geographic features at DA level in cencus year 2016. DA are small, relatively stable geographic unit composed of one or more adjacent dissemination blocks with an average population of 400 to 700 persons. It's downloaded from Statistics Canada.
### 3. Postal Code Conversion File (PCCF)
The PCCF provides a correspondence between the Canada postal code and geographic areas.
### 4. Road network data
This is transportation feature of topographic data at the scale of 1:50 000, in 2017.   
### 5. General Transit Feed Specification (GTFS) data
A series of text files collected in a ZIP file. Each file models a particular aspect of transit information: stops, routes, trips and other schedule data.
### 6. Population data
This is an excel table contains population information in census year 2016. It's downloaded from Statistics Canada.

## Preprocessing Steps
The preprocessing steps are as follows:
### 1. Divide the CT and DA data into provinces/territories and project them to North_America_Albers_Equal_Area_Conic
Because the size of the dataset for whole Canada is large, it's easier to work with data at province/territory level. Projecting to the equal area coordinate system is because this coordinate system preserves areas and we will calculate area in the following steps.
### 2. Create population data table for each province/territory
### 3. Table joint between DA data and population data, calculate and add population density, population as new fields in DA attribute table
### 4. Create a summary table to calculate the population in each CT
### 5. Table join between CT and the summary table from step 4
### 6. Calculate the population density for CT, add population density, population as new fields in CT attribute table
### 7. Project DA and CT data to North_America_Equidistant_Conic
Later we will calculate distance, projecting to this coordinate system will get a more accurate result of distance.
### 8. Create CT and DA for cities using "select by attribute"
### 9. Create PCCF point feature and clip by the CT boundary
### 10. Create roads network for cities 
   * Project the input data to North_America_Equidistant_Conic coordinate system
   * Clip the roads segment data using CT for cities boundaries, get roads line feature for cities
   * In Catalog, right click the roads line feature, click “New Network Dataset”, and notice that the network dataset can be only created based on shapefile. 
### 11. Download GTFS data for each city
This step can be done either by the script or manually, but it's important to check the format and the name of the files.

## Steps (Demonstrated by the flow chart)
### 1.	Estimation of the Service Frequency (SF) at each public transport access point from the timetables of each mode during the morning peak hours from 7 am to 9 am.
### 2.	Walking Time (WT) calculations from the POI to the closest Service Access Point (SAP). 
### 3.	Calculating Total Access Time (TAT) that combines the WT and the Average Waiting Time (AWT).
### 4.	Calculating Equivalent Doorstep Frequency (EF) for each point by dividing 30 (minutes) by TAT. 
### 5.	Estimation of the Weighted Equivalent Frequency (WEF) as a sum of all EDFs with a weighting factor in favour of the most dominant mode. 
### 6.	Calculation of the ratios between population densities in walk catchments areas and CT.
### 7.	Calculate the PTAI


## References
   * 2016 Census - Boundary files. (2016). Retrieved from Statistics Canada: http://www.statcan.gc.ca/
   * 2016 Census Profiles Files. (2016). Retrieved from Canadian Census Analyser (CHASS): http://datacentre.chass.utoronto.ca/census/
   * Saghapour, T. e. (2016). Public Transport Accessibility in Metropolitan Areas: A New Approach Incorporating Population Density. Journal of Transport Geography, 54, 273-285. doi:10.1016/j.jtrangeo.2016.06.019
   * Transport networks in Canada - CanVec. (2017). Retrieved from Government of Canada: http://ftp.maps.canada.ca/pub/nrcan_rncan/vector/canvec/shp/Transport/
   * Unit Greater Manchester Transportation. (2018). Retrieved from http://www.gmtu.gov.uk/gmbusroute/GMAL%20Calculation%20Guide.pdf


