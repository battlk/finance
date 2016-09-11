MEGA_CAP_LOWER_BOUND = 200000000000
LARGE_CAP_LOWER_BOUND = 10000000000
MID_CAP_LOWER_BOUND = 2000000000
SMALL_CAP_LOWER_BOUND = 300000000
MICRO_CAP_LOWER_BOUND = 50000000


class Stock:
	def __init__(self, symbol, name, exchange):
		self.symbol = symbol
		self.name = name
		self.exchange = exchange
		self.marketCap = 0
		self.price = 0
		self.priceToBook = 0
		self.priceToEarnings = 0
		self.priceToSales = 0
		self.dividendYield = 0
		self.capClass = "NonStock"
		self.enterpriseValue = 0
		self.EBITDA_EnterpriseValue = 0
		self.EBITDA = 0
		self.operatingCashFlow = 0
		self.priceToCashFlow = 0
		self.priceClose3Month = 0
		self.appreciation3Month = 0
		self.priceClose6Month = 0
		self.appreciation6Month = 0
		self.priceClose12Month = 0
		self.appreciation12Month = 0

	def convertNumeral(self, numeral):
		numeral = numeral.replace(',', "")

		if numeral[-1] == 'T'or numeral[-1] == "t":
			return int(float(numeral[:-1]) * 1000000000000)
		elif numeral[-1] == 'B'or numeral[-1] == "b":
			return int(float(numeral[:-1]) * 1000000000)
		elif numeral[-1] == 'M'or numeral[-1] == "m":
			return int(float(numeral[:-1]) * 1000000)
		elif numeral[-1] == 'K' or numeral[-1] == "k":
			return int(float(numeral[:-1]) * 1000)
		else:
			return float(numeral)

	def setPrice(self, price):
		self.price = price

	def setPriceToBook(self, priceToBook):
		self.priceToBook = priceToBook

	def setPriceToEarnings(self, priceToEarnings):
		self.priceToEarnings = priceToEarnings

	def setPriceToSales(self, priceToSales):
		self.priceToSales = priceToSales

	def setDividendYield(self, dividendYield):
		self.dividendYield = dividendYield

	def setEnterpriseValue(self, enterpriseValue):
		self.enterpriseValue = self.convertNumeral(enterpriseValue)

	def setEBITDA(self, EBITDA):
		self.EBITDA = self.convertNumeral(EBITDA)

	def setEBITDA_EnterpriseValue(self):
		if self.EBITDA != 0 and self.enterpriseValue != 0:
			self.EBITDA_EnterpriseValue = self.EBITDA / float(self.enterpriseValue)

	def setOperatingCashFlow(self, operatingCashFlow):
		self.operatingCashFlow = self.convertNumeral(operatingCashFlow)
		if self.operatingCashFlow != 0:
			self.priceToCashFlow = self.marketCap / float(self.operatingCashFlow)

	def setPriceToCashFlow(self, priceToCashFlow):
		self.priceToCashFlow = self.convertNumeral(priceToCashFlow)

	def set3MonthClose(self, priceClose3Month):
		self.priceClose3Month = priceClose3Month
		self.appreciation3Month = self.price - priceClose3Month

	def set6MonthClose(self, priceClose6Month):
		self.priceClose6Month = priceClose6Month
		self.appreciation6Month = self.price - priceClose6Month

	def set12MonthClose(self, priceClose12Month):
		self.priceClose12Month = priceClose12Month
		self.appreciation12Month = self.price - priceClose12Month

	def addMarketCap(self, marketCap):
		self.marketCap = self.convertNumeral(marketCap)
		self.determineCapClass()

	def determineCapClass(self):
		if self.marketCap >= MEGA_CAP_LOWER_BOUND:
			self.capClass = "Mega"
		elif self.marketCap >= LARGE_CAP_LOWER_BOUND:
			self.capClass = "Large"
		elif self.marketCap >= MID_CAP_LOWER_BOUND:
			self.capClass = "Mid"
		elif self.marketCap >= SMALL_CAP_LOWER_BOUND:
			self.capClass = "Small"
		elif self.marketCap >= MICRO_CAP_LOWER_BOUND:
			self.capClass = "Micro"
		elif self.marketCap >= 0:
			self.capClass = "Nano"


class Scorecard:
	def __init__(self, symbol):
		self.symbol = symbol
		self.priceToEarningsScore = 0
		self.priceToBookScore = 0
		self.priceToSalesScore = 0
		self.dividendYieldScore = 0
		self.priceToCashFlowScore = 0
		self.EBITDA_EVScore = 0

	def getTotalScore(self):
		return self.priceToEarningsScore + self.priceToBookScore + self.priceToSalesScore \
			+ self.dividendYieldScore + self.priceToCashFlowScore + self.EBITDA_EVScore

	def setPEScore(self, priceToEarningsScore):
		self.priceToEarningsScore = priceToEarningsScore

	def setPBScore(self, priceToBookScore):
		self.priceToBookScore = priceToBookScore

	def setPSScore(self, priceToSalesScore):
		self.priceToSalesScore = priceToSalesScore

	def setDYScore(self, dividendYieldScore):
		self.dividendYieldScore = dividendYieldScore

	def setPCScore(self, priceToCashFlowScore):
		self.priceToCashFlowScore = priceToCashFlowScore

	def setEB_EVScore(self, EBITDA_EVScore):
		self.EBITDA_EVScore = EBITDA_EVScore
