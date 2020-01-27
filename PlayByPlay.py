import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import urllib.request
import requests_html

with requests_html.HTMLSession() as session:
    resp = session.get('https://www.ncaa.com/game/3518260/play-by-play')

resp.html.render()

full_html = resp.html.html

soup = BeautifulSoup(full_html)
table = soup.find_all("tbody")

columns = ['team', 'play', 'score']
plays = pd.DataFrame(columns=columns)

for row in table[-1].find_all("tr"):
    td = row.find_all("td")
    observation = [td[0].text, td[1].text, td[2].text]
    line_dict = dict(zip(columns, observation))
    plays = plays.append(line_dict, ignore_index=True)

print(plays)

f = open("test_html.html", "w")
f.write(full_html)
f.close
