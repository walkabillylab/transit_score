
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

1. Saghapour, Tayebeh, et al. “Public Transport Accessibility in Metropolitan Areas: A New Approach Incorporating Population Density.” Journal of Transport Geography, vol. 54, 2016, pp. 273–285., doi:10.1016/j.jtrangeo.2016.06.019.

## Input Data 
The input data for calculating the PTAI are as follows:
### 1. Geographic data at Census Tract (CT) level
This is a shapefile contains geographic features at CT level in cencus year 2016. CT are small, relatively stable geographic areas that have a population of less than 10, 000. It's downloaded from Statistics Canada. 
### 2. Geographic data at Dissemination Area (DA) level
This is a shapefile contains geographic features at DA level in cencus year 2016. DA are small, relatively stable geographic unit composed of one or more adjacent dissemination blocks with an average population of 400 to 700 persons. It's downloaded from Statistics Canada.
### 3. Postal Code Conversion File (PCCF)
The PCCF provides a correspondence between the Canada postal code and geographic areas.
### 4. Road network data
This is transportation feature of topographic data.  
### 5. General Transit Feed Specification (GTFS) data
A series of text files collected in a ZIP file. Each file models a particular aspect of transit information: stops, routes, trips and other schedule data.
### 6. Population data
This is an excel table contains population information in census year 2016. It's downloaded from Statistics Canada.

## Preprocessing Steps
The preprocessing steps are as follows:
### 1. Divide the CT and DA data into provinces/territories
Because the size of the dataset for whole Canada is large, it's easier to work with data at province/territory level
### 2. 

Each step is explained in detail in the following:
