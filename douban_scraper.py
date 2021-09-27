import requests  # For downloading the HTML content using HTTP GET request
from bs4 import BeautifulSoup  # For parsing the HTML content and searching through the HTML
import os
import pandas as pd
import json
import re

url = 'https://movie.douban.com/top250?start={}&filter='
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'}

r = requests.get(url.format(0), headers=headers)
r.raise_for_status()
doc = BeautifulSoup(r.text, 'lxml')
movies = doc.find_all('li')[18:]

top_250 = []
pattern = '[0-9]{4}'

# 10 pages
for i in range(10):
    start_index = i * 25
    curr_url = url.format(start_index)
    r = requests.get(curr_url, headers=headers)
    r.raise_for_status()
    doc = BeautifulSoup(r.text, 'lxml')
    movies = doc.find_all('li')[18:]

    for movie in movies:
        movie_info = {}

        title = movie.find_all('span', attrs={'class': 'title'})
        cn_title = title[0].get_text()
        if len(title) > 1:
            raw_title = title[1].get_text().replace(u'\xa0', u' ')
            movie_info['title'] = cn_title + raw_title
        else:
            movie_info['title'] = cn_title

        info = movie.find('p', attrs={'class': ''})
        info_text = info.get_text()
        match = re.search(pattern, info_text)
        info_text = info_text[match.start():].replace(u'\xa0', u' ').strip()
        info_text = info_text.split(' / ')

        movie_info['year'] = info_text[0]
        movie_info['country'] = info_text[1]
        movie_info['type'] = info_text[2]
        top_250.append(movie_info)

f = open('douban_top250.txt', 'w', encoding='utf-8')

for movie in top_250:
    values = movie.values()
    line = '\t'.join(values) + '\n'
    f.write(line)

f.close()
