from lxml import html
import requests

page = requests.get("http://www.msn.com/en-us/money/stockdetails/analysis/fi-126.1.AAPL.NAS")
page2 = requests.get("http://www.msn.com/en-us/money/stockdetails/financials/fi-126.1.AAPL.NAS")
tree = html.fromstring(page.content)
tree2 = html.fromstring(page2.content)

test_string = tree.xpath('//p[@title="EBITDA"]/following::p[1]/text()')
test_string2 = tree.xpath('//p[@title="Enterprise Value"]/following::p[1]/text()')
test_string3 = tree2.xpath('//div[@id="price-cashflow"]/text()')
# ev = tree.xpath('//td[@class="yfnc_tabledata1"]/text()')[0]
# ev_ebitda = tree.xpath('//td[@class="yfnc_tabledata1"]/text()')[7]
# ebitda = tree.xpath('//td[@class="yfnc_tabledata1"]/text()')[18]
# cash = tree.xpath('//td[@class="yfnc_tabledata1"]/text()')[28]

# ev = [0]
# ev/ebitda [7]
# ebitda[18]
# cash flow [28]]

print test_string
print test_string2
print test_string3
# print ev
# print ev_ebitda
# print ebitda
# print cash
