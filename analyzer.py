import csv
import os
import time

from stock import Scorecard


class StockAnalyzer(object):
	def __init__(self, stockInputFileName, stockOutputFileName):
		self.dataFolderName = "Data/%s" % time.strftime('%m_%d_%y')
		if not os.path.exists(self.dataFolderName + "/Analyzed"):
			os.mkdir(self.dataFolderName + "/Analyzed")

		self.stockInputFileName = self.dataFolderName + "/Aggregate/" + stockInputFileName
		self.stockOutputFileName = self.dataFolderName + "/Analyzed/" + stockOutputFileName

	def parseFile(self, readConversionFunction):
		stockList = []
		with open(self.stockInputFileName, "rb") as stockInputFile:
			for row in csv.reader(stockInputFile):
				if len(row) > 0 and row[0] != '' and "Stocks" not in row[0]:
					row = row[:-1]
					if len(row) > 7:
						readConversionFunction(row)
					else:
						readConversionFunction(row)
					stockList.append(row)

		return stockList

	def writeFile(self, stockList, writeConversionFunction):
		with open(self.stockOutputFileName, "w") as stockOutputFile:
			for line in stockList:
				writeConversionFunction(line)
				stockOutputFile.write(','.join(line))
				stockOutputFile.write('\n')


class BigStockAnalyzer(StockAnalyzer):
	def __init__(self):
		StockAnalyzer.__init__(self, "aggregate_big_stocks.csv", "analyzed_big_stocks.csv")
		self.parseFile()
		self.initializeScoreCardMap()

	def parseFile(self):
		self.stockList = StockAnalyzer.parseFile(self, self.parseConvert)
		self.initializeScoreCardMap()

	def initializeScoreCardMap(self):
		self.scoreCardMap = {}
		for stock in self.stockList:
			self.scoreCardMap[stock[0]] = Scorecard(stock[0])

	def parseConvert(self, row):
		row[3] = float(row[3])
		row[4] = float(row[4])
		row[5] = float(row[5])
		row[6] = float(row[6])
		row[7] = float(row[7])
		row[8] = float(row[8])
		row[9] = float(row[9])

	def analyzeList(self):
		self.analyzePE()
		self.analyzePS()
		self.analyzePB()
		self.analyzePC()
		self.analyzeDY()
		self.analyzeEB_EV()

		for stock in self.stockList:
			stock.append(self.scoreCardMap[stock[0]].getTotalScore())

		self.stockList.sort(key=lambda row: row[10], reverse=True)

		decileOneUpperBound = len(self.stockList) / 10
		self.condensedList = self.stockList[:decileOneUpperBound]
		self.condensedList.sort(key=lambda row: row[9], reverse=True)

	def analyzePE(self):
		zeroPEList = []
		nonZeroPEList = []
		for stock in self.stockList:
			if stock[3] == 0:
				zeroPEList.append(stock)
			else:
				nonZeroPEList.append(stock)

		nonZeroPEList.sort(key=lambda row: row[3], reverse=False)
		peList = nonZeroPEList + zeroPEList

		for index in range(0, len(peList) - 1):
			score = self.determineScore((float(index) + 1) / len(peList))
			self.scoreCardMap[peList[index][0]].setPEScore(score)

	def analyzePS(self):
		zeroPSList = []
		nonZeroPSList = []
		for stock in self.stockList:
			if stock[5] == 0:
				zeroPSList.append(stock)
			else:
				nonZeroPSList.append(stock)

		nonZeroPSList.sort(key=lambda row: row[5], reverse=False)

		for stock in zeroPSList:
			self.scoreCardMap[stock[0]].setPSScore(5)

		for index in range(0, len(nonZeroPSList) - 1):
			score = self.determineScore((float(index) + 1) / len(nonZeroPSList))
			self.scoreCardMap[nonZeroPSList[index][0]].setPSScore(score)

	def analyzePB(self):
		zeroPBList = []
		nonZeroPBList = []
		for stock in self.stockList:
			if stock[4] == 0:
				zeroPBList.append(stock)
			else:
				nonZeroPBList.append(stock)

		nonZeroPBList.sort(key=lambda row: row[4], reverse=False)
		pbList = nonZeroPBList + zeroPBList

		for index in range(0, len(pbList) - 1):
			score = self.determineScore((float(index) + 1) / len(pbList))
			self.scoreCardMap[pbList[index][0]].setPBScore(score)

	def analyzePC(self):
		zeroPCList = []
		nonZeroPCList = []
		for stock in self.stockList:
			if stock[8] == 0:
				zeroPCList.append(stock)
			else:
				nonZeroPCList.append(stock)

		nonZeroPCList.sort(key=lambda row: row[8], reverse=False)

		for stock in zeroPCList:
			self.scoreCardMap[stock[0]].setPCScore(5)

		for index in range(0, len(nonZeroPCList) - 1):
			score = self.determineScore((float(index) + 1) / len(nonZeroPCList))
			self.scoreCardMap[nonZeroPCList[index][0]].setPCScore(score)

	def analyzeDY(self):
		zeroDYList = []
		nonZeroDYList = []
		for stock in self.stockList:
			if stock[6] == 0:
				zeroDYList.append(stock)
			else:
				nonZeroDYList.append(stock)

		nonZeroDYList.sort(key=lambda row: row[6], reverse=True)
		dividendYieldList = nonZeroDYList + zeroDYList

		for index in range(0, len(dividendYieldList) - 1):
			score = self.determineScore((float(index) + 1) / len(dividendYieldList))
			self.scoreCardMap[dividendYieldList[index][0]].setDYScore(score)

	def analyzeEB_EV(self):
		zeroEB_EVList = []
		nonZeroEB_EVList = []
		for stock in self.stockList:
			if stock[7] == 0:
				zeroEB_EVList.append(stock)
			else:
				nonZeroEB_EVList.append(stock)

		nonZeroEB_EVList.sort(key=lambda row: row[7], reverse=True)

		for stock in zeroEB_EVList:
			self.scoreCardMap[stock[0]].setEB_EVScore(5)

		for index in range(0, len(nonZeroEB_EVList) - 1):
			score = self.determineScore((float(index) + 1) / len(nonZeroEB_EVList))
			self.scoreCardMap[nonZeroEB_EVList[index][0]].setEB_EVScore(score)

	def determineScore(self, indexValue):
		if indexValue < 1:
			return 11 - indexValue * 10
		else:
			return 1

	def writeConvert(self, line):
		line[3] = str(line[3])
		line[4] = str(line[4])
		line[5] = str(line[5])
		line[6] = str(line[6])
		line[7] = str(line[7])
		line[8] = str(line[8])
		line[9] = str(line[9])
		line[10] = str(line[10])

	def writeFile(self):
		StockAnalyzer.writeFile(self, self.condensedList, self.writeConvert)


class SmallStockAnalyzer(StockAnalyzer):
	def __init__(self):
		StockAnalyzer.__init__(self, "aggregate_small_stocks.csv", "analyzed_small_stocks.csv")
		self.parseFile()

	def parseFile(self):
		self.stockList = StockAnalyzer.parseFile(self, self.parseConvert)

	def parseConvert(self, row):
		row[3] = float(row[3])
		row[4] = float(row[4])
		row[5] = float(row[5])
		row[6] = float(row[6])

	def analyzeList(self):
		nonZeroPBList = []
		for stock in self.stockList:
			if stock[3] > 0:
				nonZeroPBList.append(stock)

		nonZeroPBList.sort(key=lambda row: row[3], reverse=False)

		size = len(nonZeroPBList)
		cutoff = size / 3
		nonZeroPBList = nonZeroPBList[:cutoff]

		condensedList = []
		for line in nonZeroPBList:
			if line[4] >= 0 and line[5] >= 0:
				condensedList.append(line)

		condensedList.sort(key=lambda row: row[6], reverse=True)

		self.analyzedList = condensedList

	def writeConvert(self, line):
		line[3] = str(line[3])
		line[4] = str(line[4])
		line[5] = str(line[5])
		line[6] = str(line[6])

	def writeFile(self):
		StockAnalyzer.writeFile(self, self.analyzedList, self.writeConvert)


class MicroStockAnalyzer(StockAnalyzer):
	def __init__(self):
		StockAnalyzer.__init__(self, "aggregate_small_stocks.csv", "analyzed_micro_stocks.csv")
		self.parseFile()

	def parseFile(self):
		self.stockList = StockAnalyzer.parseFile(self, self.parseConvert)

	def parseConvert(self, row):
		row[2] = float(row[2])
		row[3] = float(row[3])
		row[4] = float(row[4])
		row[5] = float(row[5])
		row[6] = float(row[6])

	def analyzeList(self):
		nonZeroPBList = []
		for stock in self.stockList:
			if stock[3] > 0:
				nonZeroPBList.append(stock)

		nonZeroPBList = self.removeNanoStocks(nonZeroPBList)
		nonZeroPBList.sort(key=lambda row: row[3], reverse=False)

		size = len(nonZeroPBList)
		cutoff = size / 3
		nonZeroPBList = nonZeroPBList[:cutoff]

		condensedList = []
		for line in nonZeroPBList:
			if line[4] >= 0 and line[5] >= 0:
				condensedList.append(line)

		condensedList.sort(key=lambda row: row[6], reverse=True)

		self.analyzedList = condensedList

	def removeNanoStocks(self, nonZeroPBList):
		nonNanoList = []
		for stock in nonZeroPBList:
			if stock[2] >= 50000000:
				nonNanoList.append(stock)

		return nonNanoList

	def writeConvert(self, line):
		line[2] = str(line[2])
		line[3] = str(line[3])
		line[4] = str(line[4])
		line[5] = str(line[5])
		line[6] = str(line[6])

	def writeFile(self):
		StockAnalyzer.writeFile(self, self.analyzedList, self.writeConvert)


def main():
	analyzerList = [
		BigStockAnalyzer(),
		SmallStockAnalyzer(),
		MicroStockAnalyzer()
	]

	for analyzer in analyzerList:
		analyzer.analyzeList()
		analyzer.writeFile()

if __name__ == '__main__':
	main()
