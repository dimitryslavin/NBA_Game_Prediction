#!/usr/bin/env python
#Author: Dimitry Slavin (BUT not wholly my own code, read notes below)
#Name: "get_teams.py"
#Date Created: March 2015 (Estimated)
#Notes: This is not my own code. This is essentially a copy of Daniel Rodriguez's code with minor tweaks. 
#Link to Daniel Rodriguez's blog post: http://danielfrg.com/blog/2013/04/01/nba-scraping-data/
#General Purpose: Scrape NBA team names and URL prefixes from espn.com to use for later NBA stats scraping
#Detailed Purpose (Enumerated): None


import pandas as pd
import requests
from bs4 import BeautifulSoup

url = 'http://espn.go.com/nba/teams'
r = requests.get(url)

soup = BeautifulSoup(r.text)
tables = soup.find_all('ul', class_='medium-logos')

teams = []
prefix_1 = []
prefix_2 = []
teams_urls = []
for table in tables:
    lis = table.find_all('li')
    for li in lis:
        info = li.h5.a
        teams.append(info.text)
        url = info['href']
        teams_urls.append(url)
        prefix_1.append(url.split('/')[-2])
        prefix_2.append(url.split('/')[-1])


dic = {'url': teams_urls, 'prefix_2': prefix_2, 'prefix_1': prefix_1}
teams = pd.DataFrame(dic, index=teams)
teams.index.name = 'team'
teams.to_csv('teams_and_prefixes.csv')