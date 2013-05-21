"""
Read graphs in Open Street Maps osm format

Based on osm.py from brianw's osmgeocode
http://github.com/brianw/osmgeocode, which is based on osm.py from
comes from Graphserver:
http://github.com/bmander/graphserver/tree/master and is copyright (c)
2007, Brandon Martin-Anderson under the BSD License
"""

import xml.sax
import networkx
import itertools

class Node:
    def __init__(self, id, lon, lat):
        self.id = id
        self.lon = lon
        self.lat = lat
	
    def __repr__(self):
	return "Node element: id" + str(self.id)
       
class Way:
    def __init__(self, id):
        self.id = id
        self.nds = []
        self.tags = {}

    def __repr__(self):
	return "Way id: " + str(self.id) + " Node points: " + str(len(self.nds))

class OSM:
    def __init__(self, filename_or_stream):
        """ File can be either a filename or stream/file object."""
        nodes = {}
        ways = {}
        
        superself = self
        
        class OSMHandler(xml.sax.ContentHandler):
            @classmethod
            def setDocumentLocator(self,loc):
                pass
            
            @classmethod
            def startDocument(self):
                pass
                
            @classmethod
            def endDocument(self):
                pass
                
            @classmethod
            def startElement(self, name, attrs):
                if name=='node':
                    self.currElem = Node(attrs['id'], float(attrs['lon']), float(attrs['lat']))
                elif name=='way':
                    self.currElem = Way(attrs['id'])
                elif name=='tag':
		    if hasattr(self.currElem, 'tags'):
			    #Optimize by using tuples?
	                    self.currElem.tags[attrs['k']] = attrs['v']
                elif name=='nd':
                    self.currElem.nds.append(attrs['ref'])
                
            @classmethod
            def endElement(self,name):
                if name=='node':
                    nodes[self.currElem.id] = self.currElem
                elif name=='way':
                    ways[self.currElem.id] = self.currElem
                
            @classmethod
            def characters(self, chars):
                pass

        xml.sax.parse(filename_or_stream, OSMHandler)
        
        self.nodes = nodes
        self.ways = ways          

def findInlyingNodes(nodeStore, boundingbox):
	'''
		Identifies nodes whose latlng points fall inside the boundingbox.

		:param nodeStore: A dictionary containing all node objects and their corresponding latlng information.
		:param boundingbox: A list of coordinates that specify the bounding box for a particular city.
		:rtype: A set of nodes that fall inside the bounding box.
	'''
	inlyingNodes = set()
	for node in nodeStore:
		if not nodeStore.has_key(node):
			continue
		if (boundingbox['north'] >= nodeStore[node].lat >= boundingbox['south']) and (boundingbox['east'] >= nodeStore[node].lon >= boundingbox['west']):
			inlyingNodes.add(nodeStore[node].id)
	return inlyingNodes

def getNodeToWayMappings(filehandle, bbox):
	'''
		This function parses OSM XML files, strips nodes and roads that fall outside the bounding box, merges redundant roads and then creates a dictionary mapping each node (latlng point) to its corresponding road.

		:param filehandle: The OSM XML dump to read
		:param bbox: The boundingbox, the dictionary containing boundaries.
		:rtype: A dictionary mapping each node inside the boundary box to its parent road.
	'''
	big_dict = {}
	osm = OSM(filehandle)	#Parse XML file
	print "XML dump parsed"
	redundantNodes = collapseEquivalentNodes(osm.ways)
	inliers = findInlyingNodes(osm.nodes, bbox)
	while redundantNodes:
		print 'Cooking'
		newWays = {}
		for node in osm.ways:
			if osm.ways[node] in redundantNodes:
				continue
			newWays[node] = osm.ways[node]
		osm.ways = newWays
		redundantNodes = collapseEquivalentNodes(osm.ways)
	for wayNode in osm.ways.itervalues(): #list of all the ways in the list
		if 'highway' not in wayNode.tags:
			continue
		#if set(wayNode.nds).issubset(outliers):
			#continue	#All the nodes in this road are outside the bounding box
		for node in wayNode.nds:
			if node not in inliers:
				continue	#Skip outlying nodes
			if node in big_dict:
				if wayNode in big_dict[node]:
					continue	#already processed
				else:
					big_dict[node].append(wayNode)
			else:
				big_dict[node]=[wayNode]
	osm = None #optimization?
	return big_dict

def collapseEquivalentNodes(ways):
	'''
		This function merges road objects that have different IDs in the XML dump but are segments of the same road.
		This is achieved using the named-streets approach: two intersecting road objects which have the same name are merged into a single road object and the corresponding node (latlng) locations in one of the roads are copied to the other road.
		This process iterates over the list of roads and repeats the merging operation until there are no further merges possible, this is detected when the number of possible streets doesn't change on further successive merges.

		:param ways: The list of road objects to use.
		:rtype: A list of roads that are redundant and have been merged with other roads.
	'''
	nodeNames = {}
	for way in ways:
		if ways[way].tags.has_key('name'):
			streetName = ways[way].tags['name']
			if nodeNames.has_key(streetName):
				nodeNames[streetName].append(ways[way])
			else:
				nodeNames[streetName] = [ways[way]]
	equivalentStreetsList = []	#List of list containing all equiv streets
	for streetName in nodeNames:
		if len(nodeNames[streetName]) > 1:	#2 or more streets with the same name
			equivalentStreetsList.append(nodeNames[streetName])
	
	redundantNodes = set() #list of nodes to remove from graph
	for equivStreets in equivalentStreetsList:
		#processed = set()
		copiedList = list(equivStreets)
		for node in copiedList:
			intersections = [joins for joins in copiedList if joins != node and (set(node.nds) & set(joins.nds)) ]
			for ext in intersections:
				node.nds.extend(ext.nds)
				node.nds = list(set(node.nds))
				redundantNodes.add(ext)
				copiedList.remove(ext)	
	return redundantNodes


def convertMappingToGraph(nodeToWayMap):
	'''
		Creates a networkx graph from a dictionary that maps nodes to their parent roads. The dual graph (which represents roads as nodes and intersections as edges) is created by identifying intersecting roads by the presence of shared nodes (latlng) points and then creating edges between all possible combinations of intersecting roads.
		:param nodeToWayMap: A dictionary that maps nodes (latlng) points to the roads they fall in.
		:rtype: A networkx dual graph of the city.
	'''
	networkxGraph = networkx.Graph()
	for val in nodeToWayMap.itervalues():   #Get the Roads/Ways which are values in the dictionary
		if len(val) == 1:				#There is only one road pointed to by this node
			networkxGraph.add_node(val[0])
		else:
			networkxGraph.add_edges_from(itertools.combinations(val, 2))	#Add all possible combinations of two roads (intersections) as edges to the network
	nodeToWayMap = None   #Optimization?	
	return networkxGraph

def removeIsolatedNodes(graph):
	'''
		Removes zero-degree nodes from a graph

		:param graph: The networkx graph to filter
		:rtype: The list of isolated nodes in the graph
	'''
	zeroDegreeNodes = [node for node in graph if graph.degree(node) == 0]
	graph.remove_nodes_from(zeroDegreeNodes)
	return zeroDegreeNodes

def removeNodesWithSpecificHighwayTags(graph,tag):
	'''
		Removes nodes with a specific property from a graph

		:param graph: The networkx graph to filter
		:param tag: The tag to filter on
		:rtype: The list of nodes with the tag which have been removed
	'''
	nodesWithMatchingTag = getNodesWithHighWayTag(tag)
	graph.remove_nodes_from(nodesWithMatchingTag)
	return nodesWithMatchingTag

#Add function for collapsing equivalent nodes
