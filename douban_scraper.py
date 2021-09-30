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
        director_actor = info_text[:match.start()].replace(u'\xa0', u' ').strip()
        director_actor = director_actor.split('   ')
        info_text = info_text[match.start():].replace(u'\xa0', u' ').strip()
        info_text = info_text.split(' / ')

        movie_info['year'] = info_text[0]
        movie_info['country'] = info_text[1]
        movie_info['type'] = info_text[2]
        movie_info['director'] = director_actor[0][4:]
        movie_info['actor'] = director_actor[1][4:] if len(director_actor) > 1 else ''
        top_250.append(movie_info)

# transform to pandas dataframe for easy sorting
df = pd.DataFrame(top_250)

"""
some customized sorting examples
"""
# df.sort_values(by=['year'], ascending=False)
# df[df['country'].str.contains('美国')]
# df[df['type'].str.contains('科幻')]
# df[df['director'].str.contains('Christopher Nolan')]

# save data to a csv file for later use
df.to_csv('douban_top250.csv', index=False)

# or you can save to other formats such as pickle file or excel worksheet directly
# df.to_pickle('douban_top250.pkl')
# df.to_excel('douban_top250.xlsx')
