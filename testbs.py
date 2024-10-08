import json
import requests
from bs4 import BeautifulSoup

link = "https://tw.buy.yahoo.com/gdsale/gdsale.asp?gdid=10463120"

res = requests.get(link,headers={"User-Agent":"Mozilla/5.0"})
soup = BeautifulSoup(res.text,"lxml")
for homes in soup.select("script[type='application/ld+json']"):
    home_url = json.loads(homes.get_text(strip=True))
    print(home_url[0]['offers'])