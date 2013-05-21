from scipy import stats
from scipy.stats.stats import pearsonr
import pylab
from pylab import plot,show
from numpy import vstack,array
from numpy.random import rand
from scipy.cluster.vq import kmeans,vq
import pickle
from matplotlib import cm
#from framework import *
from math import *
import matplotlib.pyplot as plt
from powerlawplot import *
from powerlawfit import *
from matplotlib import cm
from scipy.interpolate import spline
from scipy import interpolate
from scipy.interpolate import interp1d
from OSMCleaner import *
from core import *
from plotter import *
from Utilities import *

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
			xPlotValues[cityName] = float(cityKeyValue)
		dictList.append(xPlotValues)
	return dictList

def readPickleData(filename):
	''' 
		Reads the pickle of processed cities data and
		returns a dictionary of cities
		
		:param filename: The pickle file
		:rtype: A list of city objects
	'''
	fl = open(filename, 'rb')
	data = pickle.load(fl)
	fl.close()
	return data

def getDataFromCities(citiesList, info, infoType):
	'''
		Retrieves information of a particular type for all the cities that have valid data 
		
		:param citiesList: A list of City Objects, might contain city objects that have invalid values
		:param info: The information to retrieve e.g. entropy, gini
		:param infoType: The type of information to retrieve, raw or Normalized
		:rtype: A dictionary linking city name to the retrieved information; this dictionary contains a dataType field specifying the kind of information it holds

	'''
	values = {}
	values['dataType'] = info
	if infoType == 'raw':
		for city in citiesList:
			if city.rawInformation['opStatus']:#Check for valid city data
				values[city.name] = city.rawInformation[info]
	else:
		for city in citiesList:
			if city.rawInformation['opStatus']:#Check for valid city data
				values[city.name] = city.normalizedInformation[info]
	return values


def findClusters(cityData, plotData, clusters):
	'''
		Runs the kmeans clustering algorithm on the data

		:param cityData: A dictionary linking city name to information e.g. entropy; this dictionary contains a dataType field specifying the kind of information it holds
		:param plotData: A dictionary linking city name to the plotting information e.g area, population; this dictionary contains a dataType field specifying the kind of information it holds
		:param clusters: The number of clusters to create
		:rtype: The collapsed city metric and plot vstack, centroids of the clusters and a list of cluster indices for each city in the data, this can be used for plotting data.
	'''
	tmp = [[cityData[city], plotData[city]] for city in cityData if plotData.has_key(city) and city != 'dataType'] #Get city and plot information for all cities that have entries in both payloads
	tmp = array(tmp)
	info = vstack(tmp)
	centroids,_ = kmeans(info, clusters)
	idx,_ = vq(info, centroids)
	return info, centroids, idx

def plotClusters(citiesVStack, clusterIndices, aggregationIndices, centroids, xlabel, ylabel):
	'''
		Creates the cluster diagrams for a list of cities based on their indices plot data

		:param citiesVStack: A vstack of city metric and plot data
		:param clusterIndicies: The cluster group for each city
		:param aggregationIndices: Aggregation information such as continent, age etc
		:param centroids: The cluster centroids
		:param fileName: The name of plots to generate
	'''

	markers = ['s', 'D', 'v', 'o', '^', 'H', 'p', '8', '<', '>' ]
	colors = ['b', 'c', 'k', 'g', 'm', 'y']
	uniqClusters = len(set(clusterIndices))
	uniqAggregations = len(set(aggregationIndices))
	#for i in range(uniqClusters):
		#pylab.scatter(citiesVStack[clusterIndices==i,0], citiesVStack[clusterIndices==i,1], marker=markers[i%9], color=colors[i%6])
	for i in range(uniqAggregations):
		pylab.scatter(citiesVStack[aggregationIndices==i,0], citiesVStack[aggregationIndices==i,1], color=colors[i%6], marker=markers[i%9], label='fdsaaaaaaaaaaaaaaaaaaaaaaaaaa')
	#plot(centroids[:,0], centroids[:,1],'sr',markersize=5, label='centroids')
	pylab.legend(loc='upper left', bbox_to_anchor=(.99,1)).draggable()
	pylab.xlabel(xlabel)
	pylab.ylabel(ylabel)
	pylab.title(ylabel + ' vs ' + xlabel)
	fileName = ylabel + ' vs ' + xlabel
	pylab.savefig(fileName + '.png', bbox_inches='tight', pad_inches=0)
	#pylab.savefig(fileName + '.pdf', bbox_inches='tight', pad_inches=0)
	#pylab.savefig(fileName + '.eps', format='eps', dpi=9000, bbox_inches='tight', pad_inches=0)
	#pylab.savefig(fileName + '.svg', format='svg', dpi=9000, bbox_inches='tight', pad_inches=0)
	show()

def getClustersTuple(listOfDictionaries, clusterName):
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
		mappingsAsIntegers[value] = (clusterGroupNum, mappings[value])
	return mappingsAsIntegers


def doPlots(payloads, processedCityData, fullClusterPayload, tagCities):
	#payload is y axis data
	#city metrics is x axis data
	#cluster is colour and shape info
	# Get valid cities
	# for each valid city, get payload data, get metric data, get cluster data
	#if in one of the five cities, make bigger and add a label
	# plot each in a scatter
	# only rawInformation exists in cities now because of new changes
	cityFields = processedCityData[0].rawInformation.keys()
	for payload in payloads:
		if payload['dataType'] not in ['crime', 'violent crime', 'property crime']:
			continue
		for key in cityFields:
			if key in ['opStatus', 'g', 'rawEntropy', 'sumEntropy', 'mean', 'stddev']:
				continue
			markers = ['s', 'D', 'v', 'o', '^', 'H', 'p', '8', '<', '>' ]
			colors = ['b', 'c', 'k', 'g', 'm', 'y', 'r']
			cities = payload.keys()
			correspondingCitiesData = [city for city in processedCityData if city.name in cities and city.rawInformation['opStatus']]
			clusterPayload = {}
			plotsForLegend = set()
			clusterTypeFound = set()
			fig = plt.figure()
			ax = plt.subplot(111)
			# Choose the plotting function based on xAxis data
			if payload['dataType'] in ['Area', 'Population']:
				plotFunction  = ax.loglog
				if key == 'gini':
					plotFunction = ax.semilogy
			else:
				plotFunction = ax.scatter
			for val in correspondingCitiesData:
				if np.isnan(val.rawInformation['entropy']) or not fullClusterPayload.has_key(val.name):
					continue
				count = fullClusterPayload[val.name][0]
				noise = count * 2
				yData = val.rawInformation[key]
				#ax.scatter(yData, payload[val.name])
				plotFunction(yData, payload[val.name], color=colors[count%7], marker=markers[count%9])
				if val.name in tagCities:
					if val.name == 'stockholm': #usually in centre so move label
						noise = -40
					plt.annotate(val.name, (yData, payload[val.name]), xytext=(20,-40+ noise), textcoords='offset points', arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.1', 
                            color='red'))
				if fullClusterPayload[val.name][1] in clusterTypeFound:
					continue
				else:
					plotsForLegend.add(val)
					clusterTypeFound.add(fullClusterPayload[val.name][1])
			for val in plotsForLegend:
				if val.name == 'district-of-columbia':
					continue
				count = fullClusterPayload[val.name][0]
				labl = fullClusterPayload[val.name][1]
				yData = val.rawInformation[key]
				plotFunction(yData, payload[val.name], color=colors[count%7], marker=markers[count%9], label=labl)
			ax.axis('tight')
			if key == 'entropy' and payload['dataType'] == 'founding century':
				ax.set_ylim(0, 22)
			if key == 'gini': #cuts off three cities/outliers but not so important
				ax.set_ylim(0.85, 1.00)
			box = ax.get_position()
			ax.legend(bbox_to_anchor=(0., 1.009999, 1., .102), loc=3,
       ncol=3, mode="expand", borderaxespad=0.)
			ax.set_ylabel(payload['dataType'])
			ax.set_xlabel(key)
			fileName = 'continent ' + payload['dataType'] + ' vs ' + key + '.png'
			plt.savefig(fileName)
			#plt.show()
			plt.close()
			

def getClusterCategoriesAndCities(clusterGroup):
	clusters = [val[1] for val in set(clusterGroup.values())]
	splitDict = {}
	for val in clusters:
		splitDict[val] = []
	for val in clusterGroup:
		category = clusterGroup[val][1]
		splitDict[category].append(val)
	return splitDict

def splinePlots(payloads, categoryToCitiesMap, processedCityData, tagCities, titleType):
	cityFields = processedCityData[0].rawInformation.keys()
	for payload in payloads:
		for key in cityFields:
			if key in ['opStatus', 'g', 'rawEntropy', 'sumEntropy', 'mean', 'stddev']:
				continue
			markers = ['s', 'D', 'v', 'o', '^', 'H', 'p', '8', '<', '>' ]
			colors = ['r', 'g', 'b', 'c', 'y', 'm', 'k']
			cities = payload.keys()
			validData = [city for city in processedCityData if city.name in cities and city.rawInformation['opStatus']]
			count = 0
			fig = plt.figure()
			ax = plt.subplot(111)
			# Choose the plotting function based on xAxis data
			if payload['dataType'] in ['Area', 'Population']:
				plotFunction  = ax.loglog
				if key == 'gini':
					plotFunction = ax.semilogx
			else:
				plotFunction = ax.plot
			for category in categoryToCitiesMap:
				categoryCityNames = categoryToCitiesMap[category]
				categoryCities = [catCity for catCity in validData if catCity.name in categoryCityNames and not np.isnan(catCity.rawInformation['entropy'])]
				xData = [payload[catCity.name] for catCity in categoryCities]
				yData =	[catCity.rawInformation[key] for catCity in categoryCities]
				sortedXData = sorted(xData)
				newY = [0] * len(xData)
				for val in sortedXData:
					i = xData.index(val)
					newY[sortedXData.index(val)] = yData[i]
				yDataNPArray = np.array(newY)
				xDataNPArray = np.array(sortedXData)
				if len(xDataNPArray) <= 3:
					continue
				tck = interpolate.splrep(xDataNPArray, yDataNPArray, k=1, s=30)
				xnew = np.linspace(xDataNPArray.min(), xDataNPArray.max(), 45)
				power_smooth = interpolate.splev(xnew,tck,der=0)
				ax.scatter(xData, yData, marker='o', color=colors[count%7])
				plotFunction(xnew, power_smooth, color=colors[count%7], label=category)
				count += 1				
			tagCityObjects = [yyy for yyy in validData if yyy.name in tagCities]
			for tagCity in tagCityObjects:
				noise = tagCityObjects.index(tagCity)
				noise *= -17
				yData = tagCity.rawInformation[key]
				plt.annotate(tagCity.name, (payload[tagCity.name], yData), xytext=(-20,-20+ noise), textcoords='offset points', arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.1', 
                            color='black'))
			ax.axis('tight')
			ax.legend(bbox_to_anchor=(0., 1.009999, 1., .102), loc=3,
       ncol=3, mode="expand", borderaxespad=0.)
			ax.set_xlabel(payload['dataType'])
			ax.set_ylabel(key)
			title = titleType + ' spline - '
			fileName = title + payload['dataType'] + ' vs ' + key + '.png'
			plt.savefig(fileName)
			#plt.show()			
			plt.close()		

def histPlots(payloads, categoryToCitiesMap, processedCityData, tagCities, titleType):
	cityFields = processedCityData[0].rawInformation.keys()
	for key in cityFields:
		if key in ['opStatus', 'g', 'rawEntropy', 'sumEntropy', 'mean', 'stddev']:
			continue
		markers = ['s', 'D', 'v', 'o', '^', 'H', 'p', '8', '<', '>' ]
		colors = ['r', 'g', 'b', 'c', 'y', 'm', 'k']
		spacing = 0.001
		count =0
		mn = 100000
		mx = -11111
		validData = [city for city in processedCityData if city.rawInformation['opStatus'] and not np.isnan(city.rawInformation['entropy'])]
		count = 0
		fig = plt.figure()
		ax = plt.subplot(111)
		dataList = {}
		weightList = []
		labels = []		
		for category in categoryToCitiesMap:
			categoryCityNames = categoryToCitiesMap[category]
			categoryCities = [catCity for catCity in validData if catCity.name in categoryCityNames]
			yData =	[catCity.rawInformation[key] for catCity in categoryCities]
			dataList[category] = yData
			#weight = np.ones_like(yData)
			#weight[:len(yData)/2] = 0.5
			#weightList.append(weight)
			#labels.append(category)
			count +=1
		for cat in dataList:
			val = dataList[cat]
			if min(val) < mn:
				mn = min(val)
			if max(val) > mx:
				mx = max(val)
		h, refbin = np.histogram(dataList[cat], 10, range=(mn,mx))
		widths = np.diff(refbin)
		spacing = (widths[0]*0.9)/len(category) #divide by 2 to use half of bin space
		#divide half of bin space by number of categories so that they are aligned
		for cat in dataList:
			val = dataList[cat]
			if len(val) == 1:
				#Remove new zealand
				print cat, len(val), colors[count%7]
				continue
			heights, bins = np.histogram(val, bins=refbin)
			normHeights = heights / float(np.sum(heights))
			ax.bar(refbin[:-1] + (count * spacing), normHeights, spacing, color=colors[count%7], label=cat)
			count += 1
		ax.axis('tight')
		ax.legend(bbox_to_anchor=(0., 1.009999, 1., .102), loc=3,
ncol=3, mode="expand", borderaxespad=0.)
		ax.set_xlabel(key)
		title = titleType + ' histogram - '
		fileName = title + key + '.png'
		plt.savefig(fileName)
		#plt.show()			
		plt.close()

def fullHistPlots(processedCityData, tagCities):
	cityFields = processedCityData[0].rawInformation.keys()
	validCities = [city for city in processedCityData if city.rawInformation['opStatus'] and not np.isnan(city.rawInformation['entropy'])]
	tagCityObjects = [yyy for yyy in validCities if yyy.name in tagCities]
	for key in cityFields:
		if key in ['opStatus', 'g', 'rawEntropy', 'sumEntropy', 'mean', 'stddev']:
			continue	
		data = [city.rawInformation[key] for city in validCities]
		mx, mn = max(data), min(data)
		heights, bins = np.histogram(data, 10, range=(mn, mx))
		widths = np.diff(bins)
		normHeights = heights / float(np.sum(heights))
		plt.bar(bins[:-1], normHeights, widths, color='#87CEFA')
		count = 0.5
		for tagC in tagCityObjects:
			val = tagC.rawInformation[key]
			name = tagC.name
			if name == 'bratislava':
				height = 0.42
				col = 'red'
			elif name == 'stockholm':
				height = 0.54
				col = 'green'
			elif name == 'new-york':
				height = 0.66
				col = 'magenta'
			elif name == 'london':
				height = 0.78
				col = 'black'
			else:
				height = 0.90
				col = 'blue'
			plt.axvline(x=val, color=col, ls='dashed')
			plt.text(val, height, tagC.name, color='black', rotation=0, size='large')
			plt.xlim(mn,mx)
		key = key[0].upper() + key[1:]
		if key == 'Cv':
			key = 'CV'
		plt.xlabel(key)
		plt.ylabel('Frequency')
		titleType = key + ' values for cities'
		plt.title(titleType)
		plt.ylim(0,1)
		#plt.axis('tight')
		plt.savefig(titleType + '.eps', format='eps', dpi=9000, bbox_inches='tight', pad_inches=0.1)
		#plt.show()
		plt.close()

def fullFits(payloads, processedCityData, tagCities):
	cityFields = processedCityData[0].rawInformation.keys()
	for payload in payloads:
		for key in cityFields:
			if key in ['opStatus', 'g', 'rawEntropy', 'sumEntropy', 'mean', 'stddev']:
				continue
			markers = ['s', 'D', 'v', 'o', '^', 'H', 'p', '8', '<', '>' ]
			colors = ['r', 'g', 'b', 'c', 'y', 'm', 'k']
			cities = payload.keys()
			validCities = [city for city in processedCityData if city.name in cities and city.rawInformation['opStatus'] and not np.isnan(city.rawInformation['entropy'])]
			count = 0
			fig = plt.figure()
			ax = plt.subplot(111)
			# Choose the plotting function based on xAxis data
			yData = [city.rawInformation[key] for city in validCities]
			xData = [payload[city.name] for city in validCities]
			if len(xData) < 5:
				continue
			sortedXData = sorted(xData)
			newY = [0] * len(xData)
			for val in sortedXData:
				i = xData.index(val)
				newY[sortedXData.index(val)] = yData[i]
			yDataNPArray = np.array(newY)
			xDataNPArray = np.array(sortedXData)
			linearInter = interp1d(xDataNPArray, yDataNPArray)
			xnew = np.linspace(min(xDataNPArray), max(xDataNPArray), 6)
			power_smooth = linearInter(xnew)
			fig = plt.figure()
			ax = plt.subplot(111)
			ax.scatter(xData, yData)
			ax.plot(xnew, power_smooth)
			tagCityObjects = [yyy for yyy in validCities if yyy.name in tagCities]
			for tagCity in tagCityObjects:
				noise = tagCityObjects.index(tagCity)
				noise *= -17
				yData = tagCity.rawInformation[key]
				#plt.annotate(tagCity.name, (payload[tagCity.name], yData), xytext=(-20,-30+ noise), textcoords='offset points', arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.1', color='red'))
			ax.axis('tight')
			ax.legend(bbox_to_anchor=(0., 1.009999, 1., .102), loc=3,
       ncol=3, mode="expand", borderaxespad=0.)
			ax.set_xlabel(payload['dataType'])
			ax.set_ylabel(key)
			title = 'Full Linear spline - '
			fileName = title + payload['dataType'] + ' vs ' + key + '.png'
			plt.savefig(fileName)
			#plt.show()			
			plt.close()

def fits(payloads, categoryToCitiesMap, processedCityData, tagCities, titleType):
	cityFields = processedCityData[0].rawInformation.keys()
	for payload in payloads:
		for key in cityFields:
			if key in ['opStatus', 'g', 'rawEntropy', 'sumEntropy', 'mean', 'stddev']:
				continue
			markers = ['s', 'D', 'v', 'o', '^', 'H', 'p', '8', '<', '>' ]
			colors = ['r', 'g', 'b', 'c', 'y', 'm', 'k']
			cities = payload.keys()
			validData = [city for city in processedCityData if city.name in cities and city.rawInformation['opStatus']]
			count = 0
			fig = plt.figure()
			ax = plt.subplot(111)
			# Choose the plotting function based on xAxis data
			if payload['dataType'] in ['Area', 'Population']:
				plotFunction  = ax.loglog
				if key == 'gini':
					plotFunction = ax.semilogx
			else:
				plotFunction = ax.plot
			for category in categoryToCitiesMap:
				categoryCityNames = categoryToCitiesMap[category]
				categoryCities = [catCity for catCity in validData if catCity.name in categoryCityNames and not np.isnan(catCity.rawInformation['entropy'])]
				xData = [payload[catCity.name] for catCity in categoryCities]
				yData =	[catCity.rawInformation[key] for catCity in categoryCities]
				sortedXData = sorted(xData)
				newY = [0] * len(xData)
				for val in sortedXData:
					i = xData.index(val)
					newY[sortedXData.index(val)] = yData[i]
				yDataNPArray = np.array(newY)
				xDataNPArray = np.array(sortedXData)
				if len(xDataNPArray) < 5:
					continue
				linearInter = interp1d(xDataNPArray, yDataNPArray, kind='cubic')
				xnew = np.linspace(xDataNPArray.min(), xDataNPArray.max(), 45)
				power_smooth = linearInter(xnew)
				ax.scatter(xData, yData, marker='o', color=colors[count%7])
				plotFunction(xnew, power_smooth, color=colors[count%7], label=category)
				count += 1				
			tagCityObjects = [yyy for yyy in validData if yyy.name in tagCities]
			for tagCity in tagCityObjects:
				noise = tagCityObjects.index(tagCity)
				noise *= -17
				yData = tagCity.rawInformation[key]
				plt.annotate(tagCity.name, (payload[tagCity.name], yData), xytext=(-20,-20+ noise), textcoords='offset points', arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.1', 
                            color='black'))
			ax.axis('tight')
			ax.legend(bbox_to_anchor=(0., 1.009999, 1., .102), loc=3,
       ncol=3, mode="expand", borderaxespad=0.)
			ax.set_xlabel(payload['dataType'])
			ax.set_ylabel(key)
			title = 'Linear spline - ' + titleType
			fileName = title + payload['dataType'] + ' vs ' + key + '.png'
			plt.savefig(fileName)
			#plt.show()			
			plt.close()

def correlation(payloads, processedCityData):
	cityFields = processedCityData[0].rawInformation.keys()
	pearson = {}
	linearReg = {}
	for payload in payloads:
		for key in cityFields:
			if key in ['opStatus', 'g', 'rawEntropy', 'sumEntropy', 'mean', 'stddev']:
				continue
			cities = payload.keys()
			validCities = [city for city in processedCityData if city.name in cities and city.rawInformation['opStatus'] and not np.isnan(city.rawInformation['entropy']) and city.name != 'as-suwayda' and city.name != 'chennai']
			yData = [city.rawInformation[key] for city in validCities]
			xData = [payload[city.name] for city in validCities]
			title = key + ' ' + payload['dataType']
			xData = np.log2(np.array(xData))
			pearson[title] = pearsonr(xData, yData)
			slope, intercept, r_value, p_value, std_err = stats.linregress(xData,yData)
			linearReg[title] = (r_value, p_value)
	return {'l':linearReg}

def linearReg(payloads, categoryToCitiesMap, processedCityData, tagCities, titleType):
	cityFields = processedCityData[0].rawInformation.keys()
	for payload in payloads:
		if payload['dataType'] not in ['property crime']:
			continue
		for key in cityFields:
			if key in ['opStatus', 'g', 'rawEntropy', 'sumEntropy', 'mean', 'stddev']:
				continue
			markers = ['s', 'D', 'v', 'o', '^', 'H', 'p', '8', '<', '>' ]
			colors = ['r', 'g', 'b', 'c', 'y', 'm', 'k']
			cities = payload.keys()
			validData = [city for city in processedCityData if city.name in cities and city.rawInformation['opStatus'] and not np.isnan(city.rawInformation['entropy']) and city.name not in ['as-suwayda', 'chennai']]
			count = 0
			fig = plt.figure()
			ax = plt.subplot(111)
			xData = [city.rawInformation[key] for city in validData]
			yData = [payload[city.name] for city in validData]
			xDataNPArray = np.array(xData)
			yDataNPArray = np.log10(np.array(yData))
			A = np.array([xDataNPArray, np.ones(len(xDataNPArray))])
			slope, intercept, r_value, p_value, std_err = stats.linregress(xDataNPArray,yDataNPArray)
			line = slope* xDataNPArray + intercept
			lstyle = '-'+colors[count%7]
			r = 'r: ' + str(r_value) + '\n'
			p = 'p: ' + str(p_value) + '\n'
			rs = 'r-squared: ' + str(r_value * r_value) + '\n'
			plotText = r + p + rs
			#err  = 'std_err: ' + str(std_err)
			ax.plot(xDataNPArray,line, lstyle, label=r)
			ax.plot(xDataNPArray,line, lstyle, label=p)
			#ax.plot(xDataNPArray,line, lstyle, label=rs)
			tag = colors[3] + markers[3]
			ax.text(xDataNPArray.min(), yDataNPArray.max()+0.06, plotText, weight='bold', bbox={'facecolor':'white', 'pad':5})
			ax.plot(xDataNPArray, yDataNPArray, tag)
			print len(xDataNPArray)
			count +=1
			ax.axis('tight')
			#ax.legend(bbox_to_anchor=(0., 1.009999, 1., .102), loc=3,ncol=3, mode="expand", borderaxespad=0.)
			ax.set_ylabel(payload['dataType'][0].upper() + payload['dataType'][1:].lower()+ " rate (scale: log10)")
			ax.set_xlabel(key[0].upper() + key[1:].lower())
			if key == 'cv':
				ax.set_xlabel("Coefficient of Variation")
			title = 'Full' + ' Linear - '
			fileName = title + key + ' vs ' + payload['dataType'] + ' (' + str(len(payload)) + ' cities).eps'
			#plt.savefig(fileName, pad_inches=0.1)
			plt.savefig(fileName, format='eps', dpi=9000, bbox_inches='tight', pad_inches=0.1)
			#plt.show()			
			plt.close()


lst = []
#citiesPickle = 'processedCities.pickle'; allTagCities
citiesPickle = 'correct'
processedCityData = readPickleData(citiesPickle)
payloads = getXPlotsListOfDictionaries('xAxisDataWithOutliers.csv')
aggregatedInfo = importListOfDictionariesFromCSV('countriesAndCities.csv')
continentAggregates = getClustersTuple(aggregatedInfo, 'continent')
structureAggregates = getClustersTuple(aggregatedInfo, 'structure')
fcAggregates = getClustersTuple(aggregatedInfo, 'founding century')
cityFields = processedCityData[0].rawInformation.keys()
tagCities = ['london', 'new-york', 'stockholm', 'bratislava', 'district-of-columbia'] #, 'as-suwayda', 'chennai']

#categoryToCitiesMap = getClusterCategoriesAndCities(structureAggregates)
#histPlots(payloads, categoryToCitiesMap, processedCityData, tagCities, 'structure')

#fullHistPlots(processedCityData, tagCities)
#amrCities = payloads[4].keys()
#americanCities = [city for city in processedCityData if city.name in amrCities]
#correlation(payloads, processedCityData)

#categoryToCitiesMap = getClusterCategoriesAndCities(continentAggregates)
#linearReg(payloads, categoryToCitiesMap, americanCities, tagCities, 'continent')

#print tagCitiess
#doPlots(payloads, processedCityData, structureAggregates, tagCities)

#fullFits(payloads, processedCityData, tagCities)

#NORM CONTINENT
#categoryToCitiesMap = getClusterCategoriesAndCities(continentAggregates)
#fits(payloads, categoryToCitiesMap, processedCityData, tagCities, 'continent')
#print tagCities
#NORM STRUCTURE
'''
categoryToCitiesMap = getClusterCategoriesAndCities(structureAggregates)
histPlots(payloads, categoryToCitiesMap, processedCityData, tagCities, 'structure')


categoryToCitiesMap = getClusterCategoriesAndCities(continentAggregates)
histPlots(payloads, categoryToCitiesMap, processedCityData, tagCities, 'continent')
#RAW CONTINENT
categoryToCitiesMap = getClusterCategoriesAndCities(continentAggregates)
splinePlots(payloads, categoryToCitiesMap, processedCityData, tagCities, 'continent', 'raw')
#print tagCities
#RAW STRUCTURE
categoryToCitiesMap = getClusterCategoriesAndCities(structureAggregates)
splinePlots(payloads, categoryToCitiesMap, processedCityData, tagCities, 'structure', 'raw')
'''
'''

#RAW CONTINENT
categoryToCitiesMap = getClusterCategoriesAndCities(continentAggregates)
splinePlots(payloads, categoryToCitiesMap, processedCityData, tagCities, 'raw')

#RAW STRUCTURE
categoryToCitiesMap = getClusterCategoriesAndCities(structureAggregates)
splinePlots(payloads, categoryToCitiesMap, processedCityData, tagCities, 'raw')
'''

'''cityFields = cities[0].rawInformation.keys()
for payload in payloads:
	for key in cityFields:
		if key == 'opStatus':
			continue
		print 'Processing', key, 'vs', payload['dataType']
		package = getDataFromCities(cities, key, 'raw')
		vertStack, centroids, clusterIndices = findClusters(package, payload, 4)
		aggregationIndices = []
		for val in vertStack:
			keyValue = val[0]
			for city in cities:
				if city.rawInformation.has_key(key):
					if city.rawInformation[key] == keyValue:
						aggregationIndices.append(continentAggregates[city.name])
						break
		aggregationIndices = array(aggregationIndices)
		plotClusters(vertStack, clusterIndices, aggregationIndices, centroids, package['dataType'], payload['dataType'])
'''

'''
payload = getXPlotsListOfDictionaries('xAxisData.csv')
area = payload[1]


validCities = [city for city in data if city.rawInformation['opStatus']]

for city in validCities:
	entropy = city.rawInformation['gini']
	if area.has_key(city.name):
		ar = area[city.name]
		lst.append([ar,entropy])

info = vstack(lst)

# computing K-Means with K = 2 (2 clusters)
centroids,_ = kmeans(info,4)
# assign each sample to a cluster
idx,_ = vq(info,centroids)

# some plotting using numpy's logical indexing
plot(info[idx==0,0],info[idx==0,1],'sb',
     info[idx==1,0],info[idx==1,1],'Dc',
     info[idx==2,0],info[idx==2,1],'vk',
     info[idx==3,0],info[idx==3,1],'og',markersize=8
)
plot(centroids[:,0],centroids[:,1],'sr',markersize=5, label='centroids')
normEnts = {}
for c in processedCityData:
	if c.rawInformation['opStatus']:
		if np.isnan(c.rawInformation['entropy']):
			print c.name, 'oops'
			continue
		n = np.log2(c.graphProperties['numNodes'])
		nn = c.rawInformation['entropy']
		normEnts[c.name] = nn

sx = sorted(normEnts.items(), key=operator.itemgetter(1))
for x in sx:
	print x[0], x[1]


for c in processedCityData:
	if c.rawInformation['opStatus'] and not np.isnan(c.rawInformation['rawEntropy']):
		c.rawInformation['normEntropy'] = c.rawInformation['rawEntropy'] / np.log2(c.graphProperties['numNodes'])



'''
