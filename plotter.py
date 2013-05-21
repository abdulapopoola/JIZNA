from math import *
import matplotlib.pyplot as plt
from powerlawplot import *
from powerlawfit import *
from matplotlib import cm

def plotPowerLaw(cityName, distribution):
	'''distribution is a list of values'''
	[alpha, xmin, L] = plfit(distribution)
	fileName = cityName + ".png"
	plplot(distribution,xmin,alpha,fileName)
	distribution = None  #Optimization?

def plotScatterPlot(allValues, fileName):
	'''allValues is a list of dictionaries containing the following fields (xValues, yValues, labels, xAxisLabel, yAxisLabel, plotTitle)'''
	numOfSubPlots = len(allValues)
	numOfRows = numOfSubPlots/2.0
	numOfCols = numOfSubPlots/numOfRows
	rows = int(ceil(numOfRows))
	cols = int(ceil(numOfCols))
	fig = plt.figure(figsize=(30,30))	
	subPlotLocation = 1	#start from the first subplot in the rows * cols grid
	for valueDict in allValues:
		subPlot = fig.add_subplot(rows, cols, subPlotLocation)
		subPlotLocation = subPlotLocation + 1
		subPlot.set_xlabel(valueDict['xAxisLabel'])
		subPlot.set_ylabel(valueDict['yAxisLabel'])
		subPlot.set_title(valueDict['plotTitle'])
		print len(valueDict['groupColorKey']), len(valueDict['xValues'])
		subPlot.scatter(valueDict['xValues'], valueDict['yValues'])		
		#subPlot.scatter(valueDict['xValues'], valueDict['yValues'], c=valueDict['groupColorKey'], cmap=cm.hot)
		allLabels = valueDict['labels']
		#for i, label in enumerate(allLabels):
			#subPlot.annotate(label, (valueDict['xValues'][i], valueDict['yValues'][i]), fontsize='xx-small')
	fig.tight_layout()	
	#fig.savefig(fileName + '.png', bbox_inches='tight', pad_inches=0)
	fig.savefig(fileName + '.pdf', bbox_inches='tight', pad_inches=0)
	#fig.savefig(fileName + '.eps', format='eps', dpi=9000, bbox_inches='tight', pad_inches=0)
	#fig.savefig(fileName + '.svg', format='svg', dpi=9000, bbox_inches='tight', pad_inches=0)
	return True
'''
a=([1,2,3],[2,4,6],['db_a','db_b','db_c'],'nums', 'doubles', 'Double') 
b=([1,2,3],[2,4,6],['db_a','db_b','db_c'],'nums', 'doubles', 'Double')
c=([2,2,3],[1,4,9],['sq_a','sq_b','sq_c'], 'nums', 'square', 'squares')
e=([4,2,3],[1,4,9],['sq_a','sq_b','sq_c'], 'nums', 'square', 'squares')
f=([7,2,3],[1,8,27],['cb_a','cb_b','cb_c'], 'nums', 'cube', 'cubes')

a = {
	'xValues': a[0],
	'yValues': a[1],
	'labels': a[2],
	'xAxisLabel': a[3],
	'yAxisLabel': a[4],
	'plotTitle': a[5]
}

b = {
	'xValues': b[0],
	'yValues': b[1],
	'labels': b[2],
	'xAxisLabel': b[3],
	'yAxisLabel': b[4],
	'plotTitle': b[5]
}
c = {
	'xValues': c[0],
	'yValues': c[1],
	'labels': c[2],
	'xAxisLabel': c[3],
	'yAxisLabel': c[4],
	'plotTitle': c[5]
}
e = {
	'xValues': e[0],
	'yValues': e[1],
	'labels': e[2],
	'xAxisLabel': e[3],
	'yAxisLabel': e[4],
	'plotTitle': e[5]
}
g=[a,b,e,c]

#plotScatterPlot(g)
#plotPowerLaw('fads', [1,2, 34, 4,5])
'''
