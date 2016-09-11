import csv
import os
import time
from threading import Thread


class StockFileAggregator(object):
	def __init__(self, nasdaqStockFileName, otherStockFileName):
		self.dataFolderName = "Data/%s" % time.strftime('%m_%d_%y')
		if not os.path.exists(self.dataFolderName + "/Aggregate"):
			os.mkdir(self.dataFolderName + "/Aggregate")

		self.nasdaqStockFileName = self.dataFolderName + "/Raw/" + nasdaqStockFileName
		self.otherStockFileName = self.dataFolderName + "/Raw/" + otherStockFileName

		self.megaCapStocks = []
		self.largeCapStocks = []
		self.midCapStocks = []
		self.smallCapStocks = []

		self.microCapStocks = []
		self.nanoCapStocks = []

		self.nonCapStocks = []
		self.rejectStocks = []

		self.capClassMap = {
			"Mega": "Mega",
			"Large": "Large",
			"Mid": "Mid",
			"Small": "Small",
			"Micro": "Micro",
			"Nano": "Nano"
		}

	def setAggregateOutputFileName(self, aggregateFileName):
		self.aggregateFileName = self.dataFolderName + "/Aggregate/" + aggregateFileName

	def determineCurrentCap(self, currentMarketCapString):
		for key in self.capClassMap.keys():
			if key in currentMarketCapString:
				return self.capClassMap[key]

	def addRecordToAppropriateList(self, currentCapBeingParsed, record):
		if currentCapBeingParsed == "Mega":
			self.megaCapStocks.append(record)
		elif currentCapBeingParsed == "Large":
			self.largeCapStocks.append(record)
		elif currentCapBeingParsed == "Mid":
			self.midCapStocks.append(record)
		elif currentCapBeingParsed == "Small":
			self.smallCapStocks.append(record)
		elif currentCapBeingParsed == "Micro":
			self.microCapStocks.append(record)
		elif currentCapBeingParsed == "Nano":
			self.nanoCapStocks.append(record)

	def loadCapStockFiles(self):
		self.loadIndividualStockFile(self.nasdaqStockFileName)
		self.loadIndividualStockFile(self.otherStockFileName)

	def loadNonCapStockFiles(self):
		self.nonCapStocks += self.loadOtherStockFile(self.nasdaqStockFileName)
		self.nonCapStocks += self.loadOtherStockFile(self.otherStockFileName)

	def loadRejectedStockFiles(self):
		self.rejectStocks += self.loadOtherStockFile(self.nasdaqStockFileName)
		self.rejectStocks += self.loadOtherStockFile(self.otherStockFileName)

	def loadIndividualStockFile(self, stockFileName):
		currentCapBeingParsed = None
		with open(stockFileName, "rb") as stockFile:
			for record in csv.reader(stockFile):
				if len(record) > 0 and record[0] != '':
					if "Stocks" in record[0]:
						currentCapBeingParsed = self.determineCurrentCap(record[0])
					else:
						self.addRecordToAppropriateList(currentCapBeingParsed, record)

	def loadOtherStockFile(self, otherStockFileName):
		stockList = []
		with open(otherStockFileName, "rb") as otherStockFile:
			for record in csv.reader(otherStockFile):
				if len(record) > 0 and record[0] != '':
					stockList.append(record)
		return stockList

	def printAggregateLargeStocksToCSV(self):
		with open(self.aggregateFileName, "w") as aggregateLargeStocksFile:
			aggregateLargeStocksFile.write("\n------------ Mega Cap Stocks --------------\n\n")
			for record in self.megaCapStocks:
				for recordItem in record:
					aggregateLargeStocksFile.write(recordItem + ",")
				aggregateLargeStocksFile.write("\n")

			aggregateLargeStocksFile.write("\n------------ Large Cap Stocks --------------\n\n")
			for record in self.largeCapStocks:
				for recordItem in record:
					aggregateLargeStocksFile.write(recordItem + ",")
				aggregateLargeStocksFile.write("\n")

			aggregateLargeStocksFile.write("\n------------ Mid Cap Stocks --------------\n\n")
			for record in self.midCapStocks:
				for recordItem in record:
					aggregateLargeStocksFile.write(recordItem + ",")
				aggregateLargeStocksFile.write("\n")

			aggregateLargeStocksFile.write("\n------------ Small Cap Stocks --------------\n\n")
			for record in self.smallCapStocks:
				for recordItem in record:
					aggregateLargeStocksFile.write(recordItem + ",")
				aggregateLargeStocksFile.write("\n")

	def printAggregateSmallStocksToCSV(self):
		with open(self.aggregateFileName, "w") as aggregateSmallStocksFile:
			aggregateSmallStocksFile.write("\n------------ Micro Cap Stocks --------------\n\n")
			for record in self.microCapStocks:
				for recordItem in record:
					aggregateSmallStocksFile.write(recordItem + ",")
				aggregateSmallStocksFile.write("\n")

			aggregateSmallStocksFile.write("\n------------ Nano Cap Stocks --------------\n\n")
			for record in self.nanoCapStocks:
				for recordItem in record:
					aggregateSmallStocksFile.write(recordItem + ",")
				aggregateSmallStocksFile.write("\n")

	def printAggregateNonCapStocksToCSV(self):
		with open(self.aggregateFileName, "w") as aggregateNonCapStocksFile:
			for record in self.nonCapStocks:
				for recordItem in record:
					aggregateNonCapStocksFile.write(recordItem + ",")
				aggregateNonCapStocksFile.write("\n")

	def printAggregateRejectedStocksToCSV(self):
		with open(self.aggregateFileName, "w") as aggregateRejectedStocksFile:
			for record in self.rejectStocks:
				for recordItem in record:
					aggregateRejectedStocksFile.write(recordItem + ",")
				aggregateRejectedStocksFile.write("\n")


class BigCapStockFileAggregator(StockFileAggregator):
	def __init__(self):
		StockFileAggregator.__init__(self, "big_cap_stocks_nasdaq.csv", "big_cap_stocks_other.csv")
		StockFileAggregator.setAggregateOutputFileName(self, "aggregate_big_stocks.csv")

	def loadFiles(self):
		StockFileAggregator.loadCapStockFiles(self)

	def printAggregatedFile(self):
		StockFileAggregator.printAggregateLargeStocksToCSV(self)


class SmallCapStockFileAggregator(StockFileAggregator):
	def __init__(self):
		StockFileAggregator.__init__(self, "small_cap_stocks_nasdaq.csv", "small_cap_stocks_other.csv")
		StockFileAggregator.setAggregateOutputFileName(self, "aggregate_small_stocks.csv")

	def loadFiles(self):
		StockFileAggregator.loadCapStockFiles(self)

	def printAggregatedFile(self):
		StockFileAggregator.printAggregateSmallStocksToCSV(self)


class NonCapStockFileAggregator(StockFileAggregator):
	def __init__(self):
		StockFileAggregator.__init__(self, "non_cap_stocks_nasdaq.csv", "non_cap_stocks_other.csv")
		StockFileAggregator.setAggregateOutputFileName(self, "aggregate_non_cap_stocks.csv")

	def loadFiles(self):
		StockFileAggregator.loadNonCapStockFiles(self)

	def printAggregatedFile(self):
		StockFileAggregator.printAggregateNonCapStocksToCSV(self)


class RejectStockFileAggregator(StockFileAggregator):
	def __init__(self):
		StockFileAggregator.__init__(self, "rejected_stocks_nasdaq.csv", "rejected_stocks_other.csv")
		StockFileAggregator.setAggregateOutputFileName(self, "aggregate_rejected_stocks.csv")

	def loadFiles(self):
		StockFileAggregator.loadRejectedStockFiles(self)

	def printAggregatedFile(self):
		StockFileAggregator.printAggregateRejectedStocksToCSV(self)


def runFileAggregator(aggregator):
	aggregator.loadFiles()
	aggregator.printAggregatedFile()


def main():
	aggregatorList = [
		BigCapStockFileAggregator(),
		SmallCapStockFileAggregator(),
		NonCapStockFileAggregator(),
		RejectStockFileAggregator()
	]

	for aggregator in aggregatorList:
		thread = Thread(target=runFileAggregator, args=(aggregator,))
		thread.start()

if __name__ == '__main__':
	main()
