#!/usr/bin/python
# -*- coding: utf-8 -*-


import sys
import re

try:
	from bs4 import BeautifulSoup
except:
	print "BS not installed"
	sys.exit()

try:
	import classes.SQL as SQL
except:
	print "Error importing MYSQL tool"
	sys.exit()

try:
	import classes.results as R
except:
	print "Error importing results tool"
	sys.exit()

try:
	import classes.morph as Morph
except:
	print "Error importing Morph tool"
	sys.exit()

try:
	from  nltk.tokenize import word_tokenize, sent_tokenize
except:
	print "Unable to import nltk.tokenize"
	sys.exit()

class Text(object):
	def __init__(self):

		#Instances
		self.sql = SQL.SQL()
		self.m = Morph.Morph()
		self.r = R.Results(cache=True)

		self.cache = True


		#Data
		self.learning = {}
		self.dots = "".join([',', '.', '...', '"', "'", ':', ';', '!', '?','-', "(", ")", "[", "]"])
		self.processed = []

		#Processed data
		f = open("./morph/stopwords.txt")
		self.stopwords = f.read().encode("UTF-8").split(",")
		f.close()

		#Reg Exp
		self.regexp = re.compile("Perseus:text:([0-9]{4}\.[0-9]{2}\.[0-9]{4})")

	def metadata(self, identifier):
		data , l = self.sql.metadata(identifier[1])
		r = { "identifier" : identifier[1]}

		if l > 0:
			for d in data:
				r[d[0]] = d[1]

		return r

	def path(self, identifier):
		p = "./texts/"
		identifier = self.regexp.search(identifier).group(1)
		#Typical data : Perseus:text:2008.01.0558
		identifier = identifier.split(".")
		p += ".".join(identifier[:2]) + "/" + ".".join(identifier) + ".xml"

		return p

	def find(self, text, forms):
		sentences = sent_tokenize(text)
		correct = []
		for form in forms:

			i = 0
			while i < len(sentences):
				#Last condition ensure that sentences has not been processed
				if form in word_tokenize(sentences[i]) and sentences[i] not in self.processed:
					self.processed.append(sentences[i])
					correct.append(sentences.pop(i))
				else:
					i += 1
		return correct

	def chunk(self, identifier, mode = "mysql"):

		if(mode == "mysql"):
			f = open(self.path(identifier[1]), "rt")
			text = f.read()
			f.close()

			self.text = text;

			return self.section(identifier)
		elif(mode == "lucene"):
			f = open(self.path(identifier), "rt")
			text = f.read()
			f.close()

			self.text = text;

			return self.section(identifier, mode = mode)


	def section(self, identifier, mode = "mysql"):
		if mode == "mysql":
			model = BeautifulSoup(identifier[8]+identifier[9])
			tags = model.find_all(True)

			t = BeautifulSoup(self.text)
			div1 = t.find(tags[-1].name, tags[-1].attrs)
			div2 = div1.find(True,{"type" : identifier[3], "n" : identifier[4]})
			if div2:

				return div2.text.encode("UTF-8")
			elif div1:
				return div1.text.encode("UTF-8")

			else:
				print identifier[1]
				print div2
				return ""
		else:
			t = BeautifulSoup(self.text)
			return t.text

	def lemmatize(self, sentence, mode = "Lemma", terms = []):
		data = []

		cached = False
		#Caching
		if self.cache == True:
			cached = self.r.sentence(sentence, boolean = True)

		if cached:
			#Loading Id of this sentence
			S = self.r.sentence(sentence)
			#Loading data
			tempData = self.r.load(S)
			data = []
			#Caching some of this data
			safe = True
			
			for row in tempData:
				m = row[1]
				self.learning[row[0]] = m
				data.append([row[0], m])
				safe = False
		else:
			#Registering sentence
			S = self.r.sentence(sentence)
			#Cleaning sentence
			sentence = sentence.strip()
			for dot in self.dots:
				sentence = sentence.replace(dot, " ")

			sentence = word_tokenize(sentence)
			safe = True
			for word in sentence:

				lower = word.lower()
				if lower not in self.stopwords:
					if word not in self.learning:
						m = self.m.morph(word)

						if m == False:
							d = False
						else:
							if self.cache == True:
								F = self.r.form(word)

								for Lem in m:
									L = self.r.lemma(Lem)

									#Make Link
									self.r.relationship(S, F, L)

							if "Auctoritas" in mode:
								m = self.m.filter(word, m, safe, terms)

							d = [word, m]
							self.learning[word] = m
					else:
						#print "Using cache for " + word
						F = self.r.form(word)

						for Lem in self.learning[word]:
							L = self.r.lemma(Lem)
							self.r.relationship(S, F, L)

						d = [word, self.learning[word]]

					if d != False:
						data.append(d)
				safe = False
		

		return data