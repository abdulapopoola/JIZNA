"""
This module contains functions that are essential 
to the automation of this framework.

It contains functions that leverage existing functionality to do the following:

* Process all OSM graph dumps in a specified directory
* Convert these processed files into networkx graphs
* Calculate the metrics for these graphs 
* Generate powerlawfit graphs if desired

This code is copyright (c) 2013, Abdulfatai Popoola under the GPL License
"""

import os
import fnmatch
from OSMCleaner import *
from core_alex import *
from plotter import *
from Utilities import *
import random
import pickle

def getAllOSMFiles(directory='.'):
	"""	getAllOSMFiles
		Retrieves all OSM files in the specified directory,
		defaults to the current directory if no directory is given.
		
		:param directory: directory to search for OSM files
		:rtype: list of all the OSM filenames
	"""
	fileNames = []
	for fileName in os.listdir(directory):
	    if fnmatch.fnmatch(fileName, '*.osm'):
        	fileNames.append(fileName)
	return fileNames

def runProcess(OSMdir, boundingBoxCSVFile, plotPowerLaws = False):
	"""	runProcess	
		Processes all OSM graphs located in a given 
		directory and returns a list of City objects.

		:param OSMdir: The directory containing OSM files
		:param boundingBoxCSVFile: A CSV file containing a list of city names and their corresponding bounding box coordinates. The city names in this CSV file **must match** the names in the OSMdir absolutely. An example is {u'west': 18.4287748, u'east': 18.9478418, u'north': 54.4472188, u'south': 54.2749559},gdansk.
		:param plotPowerLaws: Flag to determine if powerlaw fit plots will be generated for each city in the OSMdir 
		:rtype: list of processed City Objects. See :ref:`Core`
		
	"""
	OSMfiles = getAllOSMFiles(OSMdir)
	boundingData = getBoundingAreas(importListOfDictionariesFromCSV(boundingBoxCSVFile)) 
	data = []
	numFiles = str(len(OSMfiles))
	txt = " files out of " + numFiles + " processed"
	count = 0
	for OSMFileName in OSMfiles:
		cityName = OSMFileName.rsplit('.',1)[0] #Strip off characters before .; returns lagos for lagos.osm
		graph = convertMappingToGraph(getNodeToWayMappings(OSMdir + OSMFileName, boundingData[cityName]))
		print 'graph created'
		city = City(cityName, graph)
		print "City processed"
		data.append(city)
		if plotPowerLaws:
			degreeDist = [graph.degree(node) for node in graph.nodes()]
			plotPowerLaw(OSMFileName, degreeDist)
		graph = None
		city = None #Free memory?
		count += 1
		progress = str(count) + txt 
		print progress
	return data

def getPlots(data, xAxisDataDict, clusterInfo, infoType=""):
	'''Plot scatter plots for a list of City objects

	   :param data: A list of City objects. See :ref:`Core`
	   :param xAxisDataDict: A dictionary mapping city names to values for the x-Axis, city names in this dictionary **must match** the city names in the data list exactly
	   :param clusterInfo: A dictionary mapping cities to their clustering group; this is used in determing the colours to add to plots; as before, city names in this dictionary **must match** the city names in the data list exactly
	   :param infoType: The type of plots to generate; can be those of raw processed information, normalized information or both.
	   :rtype: Returns cities for which the powerlaw iteration did not converge
	'''
	#xAxisDataDict = [random.randrange(1,200) for _ in range(0, len(data))]
	rawInfo = []
	normalizedInfo = []
	powerLawDidNotConverge = [] #Cities for which the powerlaw didn't converge
	if infoType == "raw":
		for city in data:
			cityData = dict(city.rawInformation)
			cityData['name'] = city.name
			if not cityData['opStatus']:
				powerLawDidNotConverge.append(cityData)
			else:
				rawInfo.append(cityData)	
		status = drawPlots(rawInfo, xAxisDataDict, xAxisDataDict['dataType'], clusterInfo, 'Raw Cities Data vs ' + xAxisDataDict['dataType'])
	elif infoType == "normalized":
		for city in data:
			cityData = dict(city.normalizedInformation)
			cityData['name'] = city.name
			if not city.rawInformation['opStatus']:
				powerLawDidNotConverge.append(cityData)
			else:
				normalizedInfo.append(cityData)	
		status = drawPlots(normalizedInfo, xAxisDataDict, xAxisDataDict['dataType'], clusterInfo, 'Normalized Cities Data vs ' + xAxisDataDict['dataType'])
	else:	#defaults to all
		for city in data:
			normCityData = dict(city.normalizedInformation)
			normCityData['name'] = city.name
			if not city.rawInformation['opStatus']:
				powerLawDidNotConverge.append(normCityData)
			else:
				normalizedInfo.append(normCityData)				
			rawCityData = dict(city.rawInformation)
			rawCityData['name'] = city.name
			if not rawCityData['opStatus']:
				powerLawDidNotConverge.append(rawCityData)
			else:
				rawInfo.append(rawCityData)	
		status = drawPlots(normalizedInfo, xAxisDataDict, xAxisDataDict['dataType'], clusterInfo, 'Normalized Cities Data vs ' + xAxisDataDict['dataType'])
		status = drawPlots(rawInfo, xAxisDataDict, xAxisDataDict['dataType'], clusterInfo, 'Raw Cities Data vs ' + xAxisDataDict['dataType'])
	return powerLawDidNotConverge


def drawPlots(citiesInfoList, xAxisDataDict, xAxisLabel, clusterInfoDict, plotFileName):
	''' This function generates all plots based on the information given. This function generates pdf, eps and svg copies of the same plot.

	   :param citiesInfoList: A list of dictionaries containing values that will be plotted on the vertical axis'
	   :param xAxisDataDict: A dictionary mapping city names to values for the x-Axis, city names in this dictionary **must match** the city names in the data list exactly
	   :param xAxisLabel: The label for the xAxis data.
	   :param clusterInfoDict: A dictionary mapping cities to their clustering group; this is used in determing the colours to add to plots; as before, city names in this dictionary **must match** the city names in the data list exactly
	   :param plotFileName: The name for the generated plot file
	'''

	if len(xAxisDataDict) <= len(citiesInfoList): #remove 1 to remove the dataType entry which says what kind of data is in the xAxisDataDict e.g population, area
		raise "Error, number of values for xAxis does not match the number of cities: too few values"
	print "Processing Plots"
	allDataForPlots = []
	metrics = ['entropy', 'stddev', 'mean', 'cv', 'gini'] #think of range later
	for metric in metrics:
		metricValues = getValuesForAllCities(citiesInfoList, metric)
		metricLabels = [cityData[0] for cityData in metricValues] #City names
		metricValue = [cityData[1] for cityData in metricValues] #Metric values e.g. all entropy values for all cities
		xAxisData = [xAxisDataDict[cityName] for cityName in metricLabels]
		clusterList = [clusterInfoDict[cityName] for cityName in clusterInfoDict]
		#print xAxisData, metricLabels, metricValue
		metricScatterPlotData = buildScatterPlotData(xAxisData, metricValue, metricLabels, clusterList ,xAxisLabel, metric) #metric is yAxisLabel e.g entropy or stddev
		allDataForPlots.append(metricScatterPlotData)
	plotScatterPlot(allDataForPlots, plotFileName)

def getValuesForAllCities(citiesList, tag):
	''' Gets all the cities values for a tag e.g. entropy
	    citiesList is a list of city dictionaries	

	    :param citiesList: A list of processed cities.
	    :param tag: The tag to be extracted.
	    :rtype: A list of tuples with each tag containing the city name and the tag value for that city.
	'''
	value = [(city['name'], city[tag]) for city in citiesList]
	return value

def buildScatterPlotData(xAxisDataList, yAxisDataList, labels, clustersKeyList, xAxisLabel, yAxisLabel):
	'''
		Creates a dictionary containing all the data needed to make a scatter plot

		:param xAxisDataList: A list of values for the x Axis data
		:param yAxisDataList: A list of values for the y Axis data
		:param labels: labels for each entry in the lists above
		:param clustersKeyList: keys for each clustering unit for the data
		:param xAxisLabel: label for the xAxisData
		:param yAxisLabel: label for the yAxisData
		:rtype: A dictionary containing all the above values
	'''
	plotData = {}
	plotData['xValues'] = xAxisDataList
	plotData['yValues'] = yAxisDataList
	plotData['groupColorKey'] = clustersKeyList
	plotData['labels'] = labels
	title = yAxisLabel + " vs " + xAxisLabel
	plotData['plotTitle'] = title
	plotData['xAxisLabel'] = xAxisLabel
	plotData['yAxisLabel'] = yAxisLabel
	return plotData

def getXPlotsListOfDictionaries(CSVFile):
	'''
		Reads a CSV file to get all the corresponding xAxisValues for the processed cities. This information is passed to the graph plotting function to serve as data for the horizontal x Axis.
		
		:param CSVFile: CSVFile is a CSV file containing city names and their associated data such as area, population
		:rtype: A list of dictionaries for each possible city and column pairing in the CSVFile, each list corresponds to a column in the CSVFile and each dictionary in a list contains the city name and the corresponding data for that column. One of the fields in this dictionary is the dataType field which describes the kind of data this is; for example it could be area information for the cities or population.
	'''

	values = importListOfDictionariesFromCSV(CSVFile)
	keys = values[0].keys() #All column names
	dictList = []
	for key in keys:
		if key == 'city':
			continue #city name column not a datatype
		xPlotValues = {}
		xPlotValues['dataType'] = key
		for cityData in values:
			if cityData[key] == "":
				continue
			cityName = cityData['city']
			cityKeyValue = cityData[key]
			xPlotValues[cityName] = int(cityKeyValue)
		dictList.append(xPlotValues)
	return dictList

def generatePlots(xPlotsList, processedCityData, infoType=""):
	'''
		Generates plots based on processedCityData and the values for the horizontal axis.
		:param xPlotsList: A list of dictionaries corresponding to specific data. Each list holds information that will be used to represent a city on the horizontal axis. Plots will be generated for each dictionary in this list.
		:param processedCityData: A list of City objects.
		:param infoType: The type of plots to generate: raw City Information, normalized City Information or both.
		:rtype: A list of City objects which have invalid data and can not appear on plots.
	'''
	for xPlotList in xPlotsList:
		cities = xPlotList.keys()
		correspondingCitiesData = [city for city in processedCityData if city.name in cities and city.rawInformation['opStatus']]
		countryClustering = importListOfDictionariesFromCSV('countriesAndCities.csv')
		validCities = [city.name for city in correspondingCitiesData]
		fullClusterPayload = getClustersAsDict(countryClustering, 'continent')
		clusterPayload = {}
		for val in fullClusterPayload:
			if val in validCities:
				clusterPayload[val] = fullClusterPayload[val]
		print clusterPayload
		noConv = getPlots(correspondingCitiesData, xPlotList, clusterPayload, infoType)
	return noConv

data=runProcess('../', 'cityBoundaries.csv', False)

for d in data:
	print 'PICKLING',d.name
	if d.rawInformation.has_key('rawCentrality'):
		outFile=open('centrality_'+d.name+'.dat','w')
		pickle.dump((d.name,d.rawInformation['rawCentrality']),outFile)
		outFile.close()
'''
data=runProcess('../', 'cityBoundaries.csv', False)
#noConv = getPlots(data,xAxisDataDict)
fl = open('allTagCities', 'rb')
data = pickle.load(fl)
fl.close()
payload = getXPlotsListOfDictionaries('xAxisData.csv')
#generatePlots(payload, data)
'''
