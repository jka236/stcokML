import bs4 as bs
import requests

def getSPYlist():
  resp = requests.get('http://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
  soup = bs.BeautifulSoup(resp.text, 'lxml')
  table = soup.find('table', {'class': 'wikitable sortable'})
  tickers = []
  for row in table.findAll('tr')[1:]:
      ticker = row.findAll('td')[0].text
      ticker = ticker.replace("\n", "")
      ticker = ticker.replace(".", "-")
      tickers.append(ticker)
  return tickers