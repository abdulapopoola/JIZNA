nanEntropyCities = []	#Cities with nan in their entropyValues
for city in data:
	if city.rawInformation.has_key('entropy'):
		if np.isnan(city.rawInformation['entropy']):
			nanEntropyCities.append(city)

for city in nanEntropyCities:
	print city.name
	g = graphs[city.name] #Retrieve city graph
	cvs = nx.eigenvector_centrality(g, 1000) #Get centrality values
	zs = []	#list of Way nodes with zero centrality
	for cv in cvs:
		if cvs[cv] == 0:
			zs.append(cv)
	cc = nx.connected_components(g)
	others = []	#list of all nodes that are not in the giant component
	for val in cc[1:]:
		others.extend(val)
	for zCand in zs:	#check to see if any of these nodes is not in the other components
	# which means it is in the giant component; more efficient to search the other components
	# as the giant component usually contains a large percentage of nodes in the graph
		if zCand not in others:
			print zCand, city.name


dump = []
for city in processedCityData:
	if city.rawInformation['opStatus'] and not np.isnan(city.rawInformation['entropy']):
		cityDump = {}
		cityDump['city'] = city.name
		cityDump['cv'] = city.rawInformation['cv']
		cityDump['entropy'] = city.rawInformation['entropy']
		cityDump['freeman_centralization'] = city.rawInformation['freeman_centrality']
		cityDump['gini'] = city.rawInformation['gini']
		cityDump['continent'] = continentAggregates[city.name][1]
		cityDump['structure'] = structureAggregates[city.name][1]
		for payload in payloads:
			pType = payload['dataType']
			if payload.has_key(city.name):
				cityDump[pType] = payload[city.name]
			else:
				cityDump[pType] = None
		dump.append(cityDump)

exportListOfDictionariesAsCSV(dump, 'fullDump.csv')

dump = []
for city in processedCityData:
	if city.rawInformation['opStatus'] and not np.isnan(city.rawInformation['entropy']) and payloads[4].has_key(city.name):
		cityDump = {}
		cityDump['city'] = city.name
		cityDump['cv'] = city.rawInformation['cv']
		cityDump['entropy'] = city.rawInformation['entropy']
		cityDump['freeman_centralization'] = city.rawInformation['freeman_centrality']
		cityDump['gini'] = city.rawInformation['gini']
		cityDump['continent'] = continentAggregates[city.name][1]
		cityDump['structure'] = structureAggregates[city.name][1]
		for payload in payloads:
			pType = payload['dataType']
			if payload.has_key(city.name):
				cityDump[pType] = payload[city.name]
			else:
				cityDump[pType] = None
		dump.append(cityDump)

exportListOfDictionariesAsCSV(dump, 'american.csv')


for city in allR:
	if city.

yData = [x.rawInformation['gini'] for x in allR]
yData1 = [x.rawInformation['gini'] for x in allC]
yData2 = [x.rawInformation['gini'] for x in allBara]
yData3 = [x.rawInformation['gini'] for x in allG if x.rawInformation['opStatus']]

plt.plot(xData, yData, color='r', label='Random')
plt.plot(xData, yData1, color='b', label='Cycle')
plt.plot(xData, yData2,  color='g', label='Barabasi-albert')
plt.plot(xData[1:], yData3,  color='m', label='Grid')
plt.xlabel('Number of Nodes')
plt.ylabel('freeman_centrality')
plt.axis('tight')
plt.ylim(-0.1, 0.8)
plt.legend(bbox_to_anchor=(0., 1.009999, 1., .102), loc=3,
       ncol=3, mode="expand", borderaxespad=0.)
plt.savefig('Gini', format='eps', dpi=9000, bbox_inches='tight', pad_inches=0.1)
plt.show()




