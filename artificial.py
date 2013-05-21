from numpy import vstack,array
from numpy.random import rand
import pickle
from matplotlib import cm
from math import *
import matplotlib.pyplot as plt
from powerlawplot import *
from powerlawfit import *
from matplotlib import cm
from OSMCleaner import *
from core import *
from plotter import *
from Utilities import *
from random import randint
import pickle

allBara = [] #barabasi
allER = []   #Erdos
allC = [] #cycle
allG = [] #grid
allR = [] #random


startNodes = 500
endNodes = 5000
increment = 300

barabasiNodes = 5
erdosRenyiProb = 0.7
allGraphs = ['grid', 'erdos', 'cycle', 'bara', 'random']
gridXData = []
randomEdges = []

for graphType in allGraphs:
	print 'Processing ', graphType
	for i in range(startNodes, endNodes, increment):
		cityName = graphType + str(i)
		if graphType == 'bara':
			graph = nx.barabasi_albert_graph(i, barabasiNodes)
			city = City(cityName, graph)
			allBara.append(city)
		elif graphType == 'erdos':
			continue
			graph = nx.erdos_renyi_graph(i, erdosRenyiProb)
			city = City(cityName, graph)
			allER.append(city)
		elif graphType == 'cycle':
			graph = nx.cycle_graph(i)
			city = City(cityName, graph)
			allC.append(city)
		elif graphType == 'grid':
			sqt = int(ceil(sqrt(i)))
			gridXData.append(sqt*sqt)
			graph = nx.grid_2d_graph(sqt, sqt)
			city = City(cityName, graph)
			allG.append(city)
		elif graphType == 'random':
			edges = randint(i, i*i)
			randomEdges.append(edges)
			graph = nx.gnm_random_graph(i, edges)
			city = City(cityName, graph)
			allR.append(city)

xData = range(startNodes, endNodes, increment)

yData = [x.rawInformation['entropy'] for x in allR]
yData1 = [x.rawInformation['entropy']+0.001 for x in allC]
yData2 = [x.rawInformation['entropy'] for x in allBara]
yData3 = [x.rawInformation['entropy'] for x in allG if x.rawInformation['opStatus']]

plt.plot(xData, yData, color='r', label='Random')
plt.plot(xData, yData1, color='b', label='Cycle')
plt.plot(xData, yData2,  color='g', label='Barabasi-albert')
plt.plot(xData[1:], yData3,  color='m', label='Grid')
plt.xlabel('Number of Nodes')
plt.ylabel('Entropy')
plt.axis('tight')
plt.ylim(0.8, 1.1)
plt.legend(bbox_to_anchor=(0., 1.009999, 1., .102), loc=3,
       ncol=3, mode="expand", borderaxespad=0.)
plt.savefig('Entropy', format='eps', dpi=9000, bbox_inches='tight', pad_inches=0.1)
plt.show()
