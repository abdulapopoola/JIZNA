"""Some handy utilities for the graph data"""
import os, fnmatch
import urllib2
import json
import math
import csv
import ast

def getNodesWithHighWayTag(tag):
        lst = set() 
        for node in G.nodes():
                if node.tags['highway'] == tag:
                        lst.add(node)
        return lst

def getAllHighwayTagValues():
        tags = set() 
        for node in G.nodes():
                tag = node.tags['highway']
                tags.add(tag)
        return tags

def dump(collection, dumptags=False):
        for node in collection:
                if dumptags:
                        print node.tags
                else:
                        print node

def tagsOfType(tagType):
        tags = set()
        for node in G.nodes():
                if node.tags.has_key(tagType):
                        tags.add(node)
        return tags


def minDistanceBetweenTwoRoads(road1, road2):#Assume nodes have lat lon info or OSM info is available
	minDist = 6371
	for node in road1.nds:
		if not osm.nodes.has_key(node):
			continue
		ref1 = [osm.nodes[node].lat, osm.nodes[node].lon]
		for nodeRef in road2.nds:
			if not osm.nodes.has_key(nodeRef):
				continue
			ref2 = [osm.nodes[nodeRef].lat, osm.nodes[nodeRef].lon]
			if distance(ref1, ref2) < minDist:
				minDist = distance(ref1, ref2)
	return minDist

def euclideanDistance(origin, destination):
	lat1, lon1 = origin
	lat2, lon2 = destination
	radius = 6371 # km
	dlat = math.radians(lat2-lat1)
	dlon = math.radians(lon2-lon1)
	a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
	d = radius * c
	return d

def getAllOSMFiles(directory='.'):
	#uses current directory if none given
	fileNames = []
	for fileName in os.listdir(directory):
	    if fnmatch.fnmatch(fileName, '*.osm'):
        	fileNames.append(fileName[:-4]) #Strip off last 4 characters: .osm
	return fileNames

def getBoundingBoxData(city):
	urlbase = """http://maps.google.com/maps/geo?key=AIzaSyAE4nf4g5GRVw6ZJnXxe7w_b8zs-nmnFpw&q="""
	cityName = urllib2.quote(city) #Escape HTML xters
	target = urlbase + cityName
	req = urllib2.Request(target)
	opener = urllib2.build_opener()
	f = opener.open(req)
	entirePayload = json.loads(f.read())
	package = entirePayload['Placemark']
	cities = []
	for city in package:
		cityDetails = {}
		if city['AddressDetails'] and 'Country' in city['AddressDetails']:
			cityDetails['country'] = city['AddressDetails']['Country']['CountryName']
		cityDetails['cityName'] = city['address']
		cityDetails['boundingbox'] = city['ExtendedData']['LatLonBox']
		cities.append(cityDetails)
	return cities

def getMinDistancePairings(roads):
	for i in range(len(roads)): #optimize this by calling len only once
		node = roads[i]
		for nd in roads[i+1:]:
		     if minDistanceBetweenTwoRoads(node, nd) < 1:
			     print minDistanceBetweenTwoRoads(node, nd), node, nd
#Go through list once as I have already calculated the pairing for earlier matchings so there is no need to calculate for forthcoming pairs.

def exportListOfDictionariesAsCSV(listOfDictionaries, fileName):
	f = open(fileName, 'wb')
	w=csv.DictWriter(f, fieldnames=listOfDictionaries[0].keys(), delimiter=',')
	w.writeheader()
	w.writerows(listOfDictionaries)
	f.close()

def importListOfDictionariesFromCSV(csvFile):
	with open(csvFile, 'rb') as source:
		dictList = list(csv.DictReader(source, delimiter=',')) #comma-delimited CSV files only
	return dictList

def getBoundingAreas(listOfCities):
	bboxDict = {}
	for city in listOfCities:
		bboxDict[city['Address']] = ast.literal_eval(city['bbox'])
	return bboxDict

def getClustersAsDict(listOfDictionaries, clusterName):
	'''This is a list of maps that contain information in the following format
	[{'city': 'osaka', 'clusterName':'xxx'}, ...]
	'''
	mappings = {}
	for val in listOfDictionaries:
		mappings[val['city']] = val[clusterName]
	uniqueClusterGroups = list(set(mappings.values()))
	'''To make clusters appear as colours, convert each cluster into
	an integer; this will now make cities belonging to the same cluster
	have the same integer value '''
	mappingsAsIntegers = {}
	for value in mappings:
		clusterGroupNum = uniqueClusterGroups.index(mappings[value]) + 1
		mappingsAsIntegers[value] = clusterGroupNum
	return mappingsAsIntegers

"""
allCities = getAllOSMFiles('../')
bigList = []
cnt = 0
for city in allCities:
	print cnt
	data = getBoundingBoxData(city)
	bigList.extend(data)
	cnt +=1
exportListOfDictionariesAsCSV(cList, "cities")

for city in allCities:
	tmp = [node for node in cList if city.lower() in node['cityName'].lower()]
        prunedList.extend(tmp)
        print tmp
"""

