"""
This city class handles all processing and calculation of metrics for graphs.
"""
import operator
import numpy as np
import networkx as nx
from OSMCleaner import *

class City:
	'''
		City class; this takes in a graph and the name of the city
		and calculates all the information for that graph. Each city contains the following fields: name, graphProperties, rawInformation and normalizedInformation.
		Cities contain an opStatus field in their rawInformation field that indicates whether the graph for that city was processed successfully.

		:param name: The name of the city
		:param graph: The networkx graph for that city
	'''
	def __init__(self, name, graph):
		self.name = name
		removeIsolatedNodes(graph) #Do this so that the graph is mostly connected
		#self.zeroDegrees = removeIsolatedNodes(graph) #Optimization
		self.graphProperties = self.processGraphMetrics(graph)
		print "Processing Graph for ", name
		self.rawInformation = self.calcGraphInformation(graph)
		#self.fullyConnectedGraph = self.processFullyConnectedGraph(len(graph.nodes()))
		#self.normalizedInformation = {}
		#self.normalizeValues()
	
	def processGraphMetrics(self, graph):
		'''
			Calculates graph metrics like number of nodes and edges, total degree, average degree, connected components and the size of the giant components.

			:param graph: the networkx graph for a city
			:rtype: A dictionary containing processed metrics for the graph
		'''
		graphProperties = {}
		connectedComponents = nx.connected_components(graph)
		graphProperties['numEdges'] = len(graph.edges())
		graphProperties['numNodes'] = len(graph.nodes())
		if graphProperties['numNodes'] == 0:
			return graphProperties
		#graphProperties['clustering'] = nx.average_clustering(graph)
		#graphProperties['isConnected'] = nx.is_connected(graph)
		graphProperties['TotalDegree'] = float(sum(graph.degree().values()))
		graphProperties['AverageDegree'] = graphProperties['TotalDegree'] / graphProperties['numNodes']
		graphProperties['lenGiantComponent'] = len(connectedComponents[0])
		#graphProperties['ratioGiantCompToGgraph'] = float(graphProperties['lenGiantComponent']) / graphProperties['numNodes']
		graphProperties['numConnectedComponents'] = len(connectedComponents)
		return graphProperties

	def entropy(self, npArray):
		return -1.0 * np.sum(npArray * np.log2(npArray))

	def gini_coeff(self, numpyArray):
		n = len(numpyArray)
		rs = numpyArray.reshape(n,1)
		total = 0.0
		for val in rs:
			total += np.sum(abs(numpyArray - val[0]))
		gini = total / (2.0*n*n*numpyArray.mean())
		return gini	

	def processFullyConnectedGraph(self, nodesInConnGraph):
		'''
			Calculates graph metrics for a full connected graph of size nodesInConnGraph. This is used to normalize values.

			:param nodesInConnGraph: The number of nodes the fully connected graph should have.
			:rtype: A dictionary containing processed values.
		'''
		print "Processing fully connected Graph for ", self.name
		prob = 1.0 / self.graphProperties['numNodes']
		centrality = [prob] * self.graphProperties['numNodes']
		centrality_values = np.array(centrality) #Already a normalized np array
		results = {}
		results['cen'] = centrality_values
		results['entropy'] = self.entropy(centrality_values) 
		results['stddev'] = centrality_values.std()
		results['mean'] = centrality_values.mean()
		results['range'] = centrality_values.max() - centrality_values.min() #Zero is value for normalized Information so this needs fixing
		results['cv'] = results['stddev'] / results['mean']
		results['gini'] = self.gini_coeff(centrality_values)
		#Optimization ?
		centrality = None
		centrality_values = None
		distribution = None
		return results

	def calcGraphInformation(self, graph):
		''' 
			Calcuates graph metrics for the input graph

			:param graph: The graph to process.
			:rtype: A dictionary containing processed values. One of the calculations is the eigenvector centrality using the power law. If the values for a graph don't converge in less than 1000 iterations, this operation fails and the city's opStatus field will be false.
		'''
		#Calculates all the values for a graph
		results = {}
		success = True
		try: 
			centrality = nx.eigenvector_centrality(graph, 1000) #A dictionary
			
			centrality_values = np.array(centrality.values())	#numpy ndarray
			# Calculate the modulus of this vector
			magnitude = np.sqrt(centrality_values.dot(centrality_values))
			# Convert to unit vector
			unitVector = centrality_values / magnitude
			#Normalize unit vector
			unitVector /= np.sum(unitVector) 
			results['rawEntropy'] = self.entropy(unitVector)
			results['sumEntropy'] = np.sum(unitVector)
			results['g'] = graph
			# Normalize entropy by using fully connected graph; refactor and pull out of this method later
			prob = 1.0 / self.graphProperties['numNodes']
			fullyConnectedGraphCentralityValues = [prob] * self.graphProperties['numNodes']
			vals = np.array(fullyConnectedGraphCentralityValues)
			# Calculate the modulus of the vector of the fully connected Graph
			magnitude = np.sqrt(vals.dot(vals))
			# Convert to unit vector
			unitVectorFullyConnected = vals / magnitude
			#results['normSumEntropy'] = np.sum(unitVectorFullyConnected)
			#normalize
			unitVectorFullyConnected = unitVectorFullyConnected / np.sum(unitVectorFullyConnected)

			normEntropy = self.entropy(unitVectorFullyConnected) #Can use log2(N) too
			results['entropy'] = results['rawEntropy'] / normEntropy
			results['stddev'] = unitVector.std()
			unitVectorMean = unitVector.mean()
			results['mean'] = unitVectorMean * np.sqrt(self.graphProperties['numNodes'])
			results['cv'] = results['stddev'] / results['mean']
			results['gini'] = self.gini_coeff(unitVector)
			results['freeman_centrality'] = self.freeman_centrality(graph)
			#Optimization ?
			centrality = None
			centrality_values = None
			normalizedValues = None
		finally:
			if results == {}:
				success = False
			results['opStatus'] = success  #Status of calcGraphInfo
			return results

	def freeman_centrality(self, graph):
		'''
			Calculates the freeman degree centrality value for the graph

			:param graph: The graph to calculate values for
			:rtype: The centrality value for the graph, values range from 0 (for a linear graph) to 1 for a perfect star network having the same number of nodes

		'''
		deg = [graph.degree(x) for x in graph]
		degNPArray = np.array(deg)
		maxDeg = degNPArray.max()
		differences = maxDeg - degNPArray
		length = float(len(degNPArray))
		centralityValue = (np.sum(differences)) /((length -1) * (length -2))
		return centralityValue

	def normalizeValues(self):
		'''
			Normalizes city data information; this is achieved by dividing the rawInformation metrics with the data from the fully connected graph.
		'''
		inf = float('inf')
		for key in self.rawInformation:
			if key == 'opStatus':
				continue
			if self.fullyConnectedGraph[key] == 0:
				self.normalizedInformation[key] = inf
			else:			
				self.normalizedInformation[key] = float(self.rawInformation[key]) / self.fullyConnectedGraph[key]			
		
'''
bara = nx.barabasi_albert_graph(50,30)
cmpl = nx.complete_graph(20)
print "done"
u = City('bara', bara)
x = City('cmpl', cmpl)
u.normalizedInformation
'''
