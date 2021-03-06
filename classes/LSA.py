import sys

try:
	from numpy import zeros, mat, linalg
except:
	print "Unable to import Numpy"
	sys.exit()

try:
	import scipy as sp
except:
	print "Unable to import scipy"
	sys.exit()

try:
	from sklearn.cluster import spectral_clustering
except:
	print "Unable to import SkLearn"

class LSA(object):
	
	def __init__(self, nodes, edges):
		self.wdict = {}
		self.wcount = 0
		self.nodes = nodes
		self.edges = edges
		self.matrix = mat(zeros([len(self.nodes), len(self.nodes)]), int)

	def build(self):
		for node in self.nodes:
			self.wdict[node[0]] = self.wcount
			self.wcount += 1

		for edge in self.edges:
			self.matrix[self.wdict[edge[0]], self.wdict[edge[1]]] += 1
			self.matrix[self.wdict[edge[1]], self.wdict[edge[0]]] += 1

		self.matrix = self.matrix * self.matrix

		return self.matrix

	def cluster(self, building = False):
		if building == True:
			self.build()

		clustering = spectral_clustering(self.matrix)

		i = 0
		for id in clustering:
			self.nodes[i].append(int(id + 1))
			i += 1

		return self.nodes, self.edges

	def findzeros(self):
		z =0
		if 0 in self.matrix.flat:
			z += 1
		return z