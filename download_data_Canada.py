# This program is used to download data from transitfeed.com (GTFS) and uncompress the data
# The result contains a gtfs.zip file and a folder named "gtfs" with TXT files 
import arcpy
import json
import urllib2
import zipfile 


output_dir='./gtfs'

#Get links that have to be downloaded
response = urllib2.urlopen('https://api.transitfeeds.com/v1/getLocations?key=b1b09e11-f0f6-40a0-9846-766bdc72cf28')

#Convert JSON string to Python object
data = json.load(response)                                                                                         
locations=data["results"]["locations"]
links = []
for_t=0
for indexinlocations in locations:
   t = data["results"]["locations"][for_t]["t"]       #t=locations names
   
   if "Canada" in t:                                  #To download Canada-wide data
      id = data["results"]["locations"][for_t]["id"]
      print("ID is "+str(id))
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
                  print(zipLink)
                  links.append(zipLink)
               except:
                  checkid = getFeedData["results"]["feeds"][for_ty]["id"]
                  print ("The "+str(checkid+"does not have gtfs data (.zip)"))
            for_ty=for_ty+1
   for_t=for_t+1

print("links: " + str(links))
print (len(links))
linksToDownload=list(set(links))
print("Links to download = "+str(linksToDownload))
print (len(linksToDownload))


linkNumber=0
for url in linksToDownload[10:20]:                      #choose 10:20 instead of 0:
    try:
        urlToOpen = urllib2.urlopen(url)
        with open("gtfs.zip", "wb") as code:
            code.write(urlToOpen.read())

        with zipfile.ZipFile("gtfs.zip", "r") as zip_ref:
            zip_ref.extractall(output_dir)
        print(str(linkNumber) + "-----" + "GTFS data has been downloaded from LINK " + str(url))

        linkNumber=linkNumber+1
        
    except:
        print ("!!!!!!!!!!!!!!!!!!!!!!!!!!!!Check the link: "+str(linksToDownload[linkNumber]))
        print(arcpy.GetMessages())
        continue
        linkNumber=linkNumber+1
