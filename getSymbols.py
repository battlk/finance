import datetime
import os
import time
import urllib
from threading import Thread

from dateutil.relativedelta import relativedelta
import filterlists
from lxml import html
import requests

from stock import Stock
import yahoo_finance


class SymbolRetriever:
	def __init__(self, fetchUrl, symbolOutputFileName, stockExchange=None):
		self.dataFolderName = "Data/%s" % time.strftime('%m_%d_%y')
		if not os.path.exists(self.dataFolderName):
			os.makedirs(self.dataFolderName)
		if not os.path.exists(self.dataFolderName + "/Raw"):
			os.mkdir(self.dataFolderName + "/Raw")

		self.fetchUrl = fetchUrl
		self.symbolOutputFileName = self.dataFolderName + "/Raw/" + symbolOutputFileName
		self.stockList = []
		self.rejectedSymbols = []
		self.stockExchange = stockExchange

		self.exchangeSymbolMap = {
			"A": "NYSE MKT",
			"N": "NYSE",
			"P": "NYSE ARCA",
			"Z": "BATS Global Markets"
		}

	def setOutputFileNames(self, bigCapFileName, smallCapFileName, nonCapFileName, rejectedSymbolsFileName):
		self.bigCapFileName = self.dataFolderName + "/Raw/" + bigCapFileName
		self.smallCapFileName = self.dataFolderName + "/Raw/" + smallCapFileName
		self.nonCapFileName = self.dataFolderName + "/Raw/" + nonCapFileName
		self.rejectedSymbolsFileName = self.dataFolderName + "/Raw/" + rejectedSymbolsFileName

	def fetchSymbolFilesFromWeb(self):
		urllib.urlretrieve(self.fetchUrl, self.symbolOutputFileName)

	def ingestSymbolFiles(self):
		with open(self.symbolOutputFileName, "r") as symbolOutputFile:
			self.parseSymbolFile(symbolOutputFile)

		print "Length Of Stock List %s " % len(self.stockList)

	def parseSymbolFile(self, inputFile):
		line = inputFile.readline()
		while line:
			dontSaveFlag = False
			if "File Creation" not in line:
				components = line.split("|")
				symbol = components[0]

				if symbol not in filterlists.symbolBlackList:
					name = components[1].replace(',', "")

					if self.isAStockOrShare(symbol, name):
						if self.stockExchange is None:
							self.stockExchange = self.convertExchangeSymbol(components[2])

						stock = Stock(symbol, name, self.stockExchange)
						self.stockList.append(stock)
					else:
						for filterString in filterlists.badNameCharactersDontSave:
							if filterString in name:
								dontSaveFlag = True
						if not dontSaveFlag:
							self.rejectedSymbols.append([symbol, name])

			line = inputFile.readline()

	def isAStockOrShare(self, stockSymbol, stockName):
		for filterString in filterlists.badSymbolCharacters:
			if filterString in stockSymbol:
				return False

		for filterString in filterlists.badNameCharacters:
			if filterString in stockName:
				return False

		for filterString in filterlists.goodCharacters:
			if filterString in stockName:
				if "Funding" not in stockName and "Fund" in stockName:
					return False
				return True

		if ("Fund" in stockName or "Trust" in stockName) and "Municipal" not in stockName:
			for filterString in filterlists.trustFundGoodCharacters:
				if filterString in stockName:
					return True

		if self.stockExchange is None:
			for filterString in filterlists.notNasdaqGoodCharacters:
				if filterString in stockName:
					return True

		return False

	def convertExchangeSymbol(self, symbol):
		try:
			return self.exchangeSymbolMap[symbol]
		except KeyError:
			return symbol

	def gatherStockData(self):
		self.pullStockDataFromYahoo()
		self.scrapeStockDataFromMSN()
		self.stockList.sort(key=lambda stock: stock.marketCap, reverse=True)

	def pullStockDataFromYahoo(self):
		for stock in self.stockList:
			try:
				print "Getting share for: " + stock.symbol
				shareData = yahoo_finance.Share(stock.symbol)

				marketCap = str(shareData.get_market_cap())
				price = shareData.get_price()
				priceToBook = shareData.get_price_book()
				priceToSales = shareData.get_price_sales()
				priceToEarnings = shareData.get_price_earnings_ratio()
				dividendYield = shareData.get_dividend_yield()

				if marketCap != 'None':
					stock.addMarketCap(marketCap)

				if price is not None:
					stock.setPrice(float(price))
				if priceToBook is not None:
					stock.setPriceToBook(float(priceToBook))
				if priceToSales is not None:
					stock.setPriceToSales(float(priceToSales))
				if priceToEarnings is not None:
					stock.setPriceToEarnings(float(priceToEarnings))
				if dividendYield is not None:
					stock.setDividendYield(float(dividendYield))

				self.pullHistoricalDataFromYahoo(stock, shareData)
			except AttributeError as error:
				print "Could Not Find Results For %s\n %s" % (stock.symbol, error)

	def pullHistoricalDataFromYahoo(self, stock, shareData):
		today = datetime.datetime.today()
		date3MonthsAgo = str((today - relativedelta(months=3)).date())
		date6MonthsAgo = str((today - relativedelta(months=6)).date())
		date12MonthsAgo = str((today - relativedelta(months=12)).date())

		data3Months = shareData.get_historical(date3MonthsAgo, date3MonthsAgo)
		if len(data3Months) > 0:
			stock.set3MonthClose(float(data3Months[0]['Close']))

		data6Months = shareData.get_historical(date6MonthsAgo, date6MonthsAgo)
		if len(data6Months) > 0:
			stock.set6MonthClose(float(data6Months[0]['Close']))

		data12Months = shareData.get_historical(date12MonthsAgo, date12MonthsAgo)
		if len(data12Months) > 0:
			stock.set12MonthClose(float(data12Months[0]['Close']))

	def scrapeStockDataFromMSN(self):
		for stock in self.stockList:
			print "Scraping: " + stock.symbol
			analysisPage = requests.get("http://www.msn.com/en-us/money/stockdetails/analysis/fi-126.1." + stock.symbol + ".NAS")
			financialsPage = requests.get("http://www.msn.com/en-us/money/stockdetails/financials/fi-126.1." + stock.symbol + ".NAS")

			analysisHtmlTree = html.fromstring(analysisPage.content)
			financialsHtmlTree = html.fromstring(financialsPage.content)

			try:
				EBITDA = analysisHtmlTree.xpath('//p[@title="EBITDA"]/following::p[1]/text()')[0]
			except IndexError:
				EBITDA = "0"

			try:
				enterpriseValue = analysisHtmlTree.xpath('//p[@title="Enterprise Value"]/following::p[1]/text()')[0]
			except IndexError:
				enterpriseValue = "0"

			try:
				priceToCashFlow = financialsHtmlTree.xpath('//div[@id="price-cashflow"]/text()')[0]
			except IndexError:
				priceToCashFlow = "0"

			if enterpriseValue != '-':
				stock.setEnterpriseValue(enterpriseValue)
			if EBITDA != '-':
				stock.setEBITDA(EBITDA)
			stock.setEBITDA_EnterpriseValue()
			if priceToCashFlow != '-':
				stock.setPriceToCashFlow(priceToCashFlow)

	def printStocksToCSV(self):
		lastCapPrinted = "None"
		with open(self.nonCapFileName, "w") as nonFile:
			for stock in self.stockList:
					if stock.capClass == "NonStock":
						nonFile.write(
							stock.symbol + "," + stock.name + "," + str(stock.marketCap) + "," + str(stock.priceToEarnings) + "," +
							str(stock.priceToBook) + "," + str(stock.priceToSales) + "," + str(stock.dividendYield) + "," + str(stock.EBITDA) +
							"," + str(stock.enterpriseValue) + "," + str(stock.EBITDA_EnterpriseValue) + "," + str(stock.operatingCashFlow) +
							"," + str(stock.priceToCashFlow) + "," + str(stock.appreciation3Month) + "," + str(stock.appreciation6Month) + "," +
							str(stock.appreciation12Month) + "\n")

		with open(self.bigCapFileName, "w") as bigFile:
			for stock in self.stockList:
				if stock.marketCap >= 300000000:
					if stock.capClass != lastCapPrinted:
						bigFile.write("\n------------ " + stock.capClass + " Cap Stocks --------------\n\n")
						lastCapPrinted = stock.capClass

					bigFile.write(
						stock.symbol + "," + stock.name + "," + str(stock.marketCap) + "," + str(stock.priceToEarnings) +
						"," + str(stock.priceToBook) + "," + str(stock.priceToSales) + "," + str(stock.dividendYield) + "," +
						str(stock.EBITDA_EnterpriseValue) + "," + str(stock.priceToCashFlow) + "," + str(stock.appreciation6Month) + "\n")

		with open(self.smallCapFileName, "w") as smallFile:
			for stock in self.stockList:
				if stock.marketCap < 300000000:
					if stock.capClass != lastCapPrinted:
						smallFile.write("\n------------ " + stock.capClass + " Cap Stocks --------------\n\n")
						lastCapPrinted = stock.capClass

					smallFile.write(
						stock.symbol + "," + stock.name + "," + str(stock.marketCap) + "," + str(stock.priceToBook) + "," +
						str(stock.appreciation3Month) + "," + str(stock.appreciation6Month) + "," + str(stock.appreciation12Month) + "\n")

		with open(self.rejectedSymbolsFileName, "w") as rejectFile:
			for stock in self.rejectedSymbols:
				rejectFile.write(stock[0] + "," + stock[1] + "\n")


class NasdaqSymbolRetriever(SymbolRetriever):
	def __init__(self):
		SymbolRetriever.__init__(self, "ftp://ftp.nasdaqtrader.com/symboldirectory/nasdaqlisted.txt", "nasdaqlisted.txt", "NASDAQ")

		SymbolRetriever.setOutputFileNames(
			self,
			"big_cap_stocks_nasdaq.csv", "small_cap_stocks_nasdaq.csv",
			"non_cap_stocks_nasdaq.csv", "rejected_stocks_nasdaq.csv"
		)

	def retrieveSymbolData(self):
		self.fetchSymbolFilesFromWeb()
		self.ingestSymbolFiles()
		self.gatherStockData()
		self.printStocksToCSV()


class OtherSymbolRetriever(SymbolRetriever):
	def __init__(self):
		SymbolRetriever.__init__(self, "ftp://ftp.nasdaqtrader.com/symboldirectory/otherlisted.txt", "otherlisted.txt")

		SymbolRetriever.setOutputFileNames(
			self,
			"big_cap_stocks_other.csv", "small_cap_stocks_other.csv",
			"non_cap_stocks_other.csv", "rejected_stocks_other.csv"
		)

	def retrieveSymbolData(self):
		self.fetchSymbolFilesFromWeb()
		self.ingestSymbolFiles()
		self.gatherStockData()
		self.printStocksToCSV()


def runSymbolRetriever(retriever):
	symbolRetrievalComplete = False

	while not symbolRetrievalComplete:
		try:
			retriever.retrieveSymbolData()
			symbolRetrievalComplete = True
		except (yahoo_finance.YQLQueryError, requests.exceptions.ChunkedEncodingError) as error:
			print "Error Encountered: %s" % error


def main():
	retrieverList = [
		NasdaqSymbolRetriever(),
		OtherSymbolRetriever()
	]

	for retriever in retrieverList:
		thread = Thread(target=runSymbolRetriever, args=(retriever,))
		thread.start()


if __name__ == '__main__':
	main()
