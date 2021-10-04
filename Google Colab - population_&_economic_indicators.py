# -*- coding: utf-8 -*-
"""Population & Economic Indicators.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1O2lHm_Mc5YgP6VtwdO-9NJrSmoip9oO2

# Library
"""

# Mount from google drive
from google.colab import drive
drive.mount("/content/drive/", force_remount = True)

!pip install pycountry

import requests
import calendar
import pycountry
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
from datetime import date, datetime, timedelta

"""# Population based on main area calculation

"""

def get_data_from_link(link):
  soup = BeautifulSoup(requests.get(link).text,'lxml')
  cities_by_population_table = soup.find('table',{'class':"table table-hover table-condensed table-list"}).findAll('tbody')
  return cities_by_population_table[0].findAll('tr')

worldometers ='https://www.worldometers.info/world-population/'
links = [{
    "country name": "Japan",
    "link": worldometers + "japan-population/"
},
{
    "country name": "Malaysia",
    "link": worldometers + "malaysia-population/"
}]

result_df = pd.DataFrame(columns=["country_code","country_name", "area", "population"])

for i in links:
  population_df = []
  link = i["link"]
  country_name = i["country name"]
  country_data_rows = get_data_from_link(link)

  # getting country code
  country_codes = pycountry.countries.get(name=country_name)
  country_codes = [code for code in country_codes.alpha_2.split()]
  code_dict = dict(zip(country_name.split(),country_codes))
  # ','.join removing []
  country_code = ','.join([code[:] for code in code_dict.values()])

  for row in country_data_rows:
    td_tags = row.findAll('td')
    population_df.append({
      "country_code": country_code,
      "country_name": country_name,
      "area" : td_tags[1].text,
      "population" : int(td_tags[2].text.replace(",","")) 
    })

  result_df = pd.concat([result_df, pd.DataFrame(population_df)])

# drop unknown area - Honcho Japan 
result_df = result_df.drop(result_df[result_df.area == 'Honcho'].index)

# result_df

# sorting country name
result_df = result_df.sort_values('country_name')
# replacing old index with new index
result_df.reset_index(inplace = True, drop = True)

"""Japan prefecture and area list"""

# import Japan's prefecture list 
japan_prefecture_df = pd.read_csv("/content/drive/MyDrive/FPT /Population & economic indicators/Japan Prefecture - Acute Accent Removed.csv", 
            names=['area','prefecture'], sep=' *, *', skiprows=1,engine='python')
# creating country_code for prefecture dataframe
japan_prefecture_df ['country_code'] = 'JP'
# japan_prefecture_df

# japan_prefecture_df.prefecture.value_counts()

"""USA prefecture and area list"""

# import USA's states list 
usa_state_df = pd.read_csv("/content/drive/MyDrive/FPT /Population & economic indicators/USA - States and Cities.csv",engine='python')
usa_state_df = usa_state_df.rename(columns={'city':'area','state_name':'prefecture'})

# drop unnecessary columns
drop_columns = [1,2,4,5,6,7,9,10,11,12,13,14,15,16]
usa_state_df = usa_state_df.drop(usa_state_df.columns[drop_columns], axis=1)

usa_state_df ['country_code'] = 'US'
usa_state_df ['country_name'] = 'United States'

# year
usa_state_df['year'] = '2021'

usa_state_df = usa_state_df.reindex(columns=['country_code','country_name' ,'area','population','prefecture','year'])

"""Japan"""

japan_population = pd.merge(result_df, japan_prefecture_df, how='inner', on=['area','country_code'])

# year
japan_population['year'] = '2020'

# reorder columns
japan_population = japan_population.reindex(columns=['country_code','country_name' ,'area','population','prefecture','year'])

# reset index
japan_population.reset_index(inplace = True, drop = True)
# japan_population[0:5]z

"""Malaysia prefecture and area list"""

# import Malaysia's states list
malay_state_df = pd.read_csv('/content/drive/MyDrive/FPT /Population & economic indicators/Malaysia cities and states.csv', 
            names=['area','prefecture'], sep=' *, *', skiprows=1,engine='python')
malay_state_df = malay_state_df.rename(columns={'state':'prefecture','city':'area'})

malay_state_df ['country_code'] = 'MY'
malay_state_df[0:5]

result_df = result_df.drop(result_df[result_df.country_code =='JP'].index)

# concat malay population and its prefecture
malay_population = pd.concat([result_df, malay_state_df], axis=1, join="inner")

# year
malay_population['year'] = '2020'

# reset index
malay_population.reset_index(inplace = True, drop = True)

# drop duplicated columns
malay_population = malay_population.loc[:,~malay_population.columns.duplicated()]

# reorder columns
malay_population = malay_population.reindex(columns=['country_code','country_name' ,'area','population','prefecture','year'])

"""General population dataframe"""

population = pd.concat([japan_population,malay_population,usa_state_df])

# sorting ascending values
population = population.sort_values(by=['population','country_code'],ascending=False)

# timestamp
updated_at = pd.to_datetime('today').strftime("%Y-%m-%d")
population['updated_at'] = updated_at

# drop duplicated values
population = population.drop_duplicates()

# rename value
population = population.rename(columns={'prefecture':'prefecture/state'})

# drop rows where population is under 50 000 
# population = population.drop(population[population.population < 50000].index)

population = population.reindex(columns=['country_code','country_name','area','population','prefecture/state','updated_at','year'])

# reset index
population.reset_index(inplace = True, drop = True)

"""# Population based on main area results

Japan population
"""

japan_population[0:5]

"""Malaysia population"""

malay_population[0:5]

"""USA population"""

usa_state_df[0:5]

"""General population based on prefecture/state and area"""

population[0:5]

"""# CSV download"""

population.to_csv('General population based on areas.csv',encoding='utf-8')
japan_population.to_csv('Japan population based on areas.csv',encoding='utf-8')
usa_state_df.to_csv('USA population based on areas.csv',encoding='utf-8')
malay_population.to_csv('Malaysia population based on areas.csv',encoding='utf-8')

"""# Plot"""

population['population'] = pd.to_numeric(population['population'])

"""Scatter plot"""

population.plot(x='country_code', y ='population', kind = 'scatter', figsize=(5,5))
plt.show()

"""Distribution plot"""

usa_state_df.plot(x = 'prefecture',y='population', figsize=(10,5), grid=True)

japan_population.plot(x = 'prefecture',y='population', figsize=(10,5), grid=True)

malay_population.plot(x = 'prefecture',y='population', figsize=(10,5), grid=True)

"""# Test"""

# import test case
test_case = pd.read_csv('/content/drive/MyDrive/FPT /Population & economic indicators/test_case.csv', engine = 'python')

def assertEquals(test_case, population):
  test_df = test_case.assign(Availability = test_case.population.isin(population.population).astype(bool))
  # test_df = test_df.drop(test_df[test_df.Availability == True].index)
  test_df.reset_index(drop = True,inplace = True)
  return test_df
assertEquals(test_case, population)

"""# Population based on prefecture calculation

USA
"""

usa_state_pop = usa_state_df.rename(columns={'prefecture':'prefecture/state'})
usa_state_pop.groupby(['prefecture/state'])['population'].sum().reset_index()

usa_state_pop = usa_state_pop.sort_values(by=['population'],ascending=False)
usa_state_pop ['country_code'] = 'US'
usa_state_pop ['country_name'] = 'United States'

# year
usa_state_pop['year'] = '2021'

# reset columns order
usa_state_pop = usa_state_pop.reindex(columns=['country_code','country_name','population','prefecture/state','year'])

# usa_state_pop[0:10]

"""Japan"""

# crawl information from wikipedia website
# ping a website and return the HTML 
website_url = requests.get('https://en.wikipedia.org/wiki/Prefectures_of_Japan').text
soup = BeautifulSoup(website_url,'lxml')

# accessing HTML tags to locate the table
# tag class="wikitable sortable jquery-tablesorter" replace with class="wikitable sortable"
table = soup.find('table',{'class':"wikitable sortable"})
tr = table.findAll('tr')

jp_prefecture = []
pre_population = [] 
for i in tr:
  tds = i.findAll('td')
  if tds:
    jp_prefecture.append(tds[0].text.replace('\n','').replace('Ō','O').replace('ō','o').strip())
    pre_population.append(tds[6].text.replace('\n','').replace(',','').strip())
japan_pre_population = pd.DataFrame({'prefecture/state':jp_prefecture,
                                     'population':pre_population})

# Change population column type to int64
japan_pre_population['population'] = pd.to_numeric(japan_pre_population['population'])

# Sorted population value to ascending
japan_pre_population = japan_pre_population.sort_values(by=['population'],ascending=False)

# reset index
japan_pre_population.reset_index(inplace=True,drop=True)

japan_pre_population ['country_code'] = 'JP'
japan_pre_population ['country_name'] = 'Japan'

# year
japan_pre_population['year'] = '2015'

# reset columns order
japan_pre_population = japan_pre_population.reindex(columns=['country_code','country_name','population','prefecture/state','year'])
# japan_pre_population

# df['prefecture'] = df['prefecture'].astype(float)

"""Malay"""

soup_malay = BeautifulSoup(requests.get('https://en.wikipedia.org/wiki/Demographics_of_Malaysia').text,'lxml')
# there are 2 tables with the same tag, so using .find_all instead of .find or .findAll
table_malay = soup_malay.find_all('table',{'class':"toccolours sortable"})[1]
tr_malay = table_malay.findAll('tr')

malay_state = []
malay_state_pop = []

for i in tr_malay:
  td = i.findAll('td')
  th = i.findAll('th')
  # if td means some tag tr doesn't have td
  malay_state_pop.append(td[0].text.replace(',','')) if td else None
  [malay_state.append(th.text.replace('\n','').replace('FT ','')) for th in th]
  
malay_state_pop_df = pd.DataFrame({'prefecture/state':malay_state[8:],
                                   'population':malay_state_pop})
# Change population column type to int64
malay_state_pop_df['population'] = pd.to_numeric(malay_state_pop_df['population'])

# Sorted population value to ascending
malay_state_pop_df = malay_state_pop_df.sort_values(by=['population'],ascending=False)

malay_state_pop_df ['country_code'] = 'MY'
malay_state_pop_df ['country_name'] = 'Malaysia'

# year
malay_state_pop_df['year'] = '2010'

# reset columns order
malay_state_pop_df = malay_state_pop_df.reindex(columns=['country_code','country_name','population','prefecture/state','year'])

# reset index
malay_state_pop_df.reset_index(inplace=True, drop=True)
# malay_state_pop_df

"""Concat 3 dataframes"""

population_pre = pd.concat([japan_pre_population,usa_state_pop,malay_state_pop_df])

# sorting ascending values
population_pre = population_pre.sort_values(by=['population','country_code'],ascending=False)

# timestamp
updated_at = pd.to_datetime('today').strftime("%Y-%m-%d")
population_pre['updated_at'] = updated_at


# reset index
population_pre.reset_index(inplace = True, drop = True)

# remove space
population_pre['prefecture/state'].str.strip()

# reset columns order
population_pre = population_pre.reindex(columns=['country_code','country_name','population','prefecture/state','updated_at','year'])

"""# Population based on prefecture results

USA
"""

usa_state_pop[0:5]

"""Japan"""

japan_pre_population[0:5]

"""Malay"""

malay_state_pop_df[0:5]

"""Population based on prefecture of Malay, Japan, USA"""

population_pre[0:5]

"""# Total population """

total = population_pre.groupby(['country_code','country_name','updated_at'])['population'].sum().reset_index()
total = total.sort_values(by='population',ascending = False)
# reset columns order
total = total.reindex(columns=['country_code','country_name','population','updated_at'])
total.reset_index(inplace=True,drop=True)
total

"""# Plot"""

population_pre.plot(x='country_code', y ='population', kind = 'scatter', figsize=(5,5))
plt.show()

"""# Test"""

# import test case
test_case_pre = pd.read_csv('/content/drive/MyDrive/FPT /Population & economic indicators/test_case_pre.csv', engine = 'python')

def assertEquals(test_case_pre, population):
  test_pre_df = test_case_pre.assign(Availability = test_case_pre.population.isin(population_pre.population).astype(bool))
  test_pre_df = test_pre_df.drop(test_pre_df[test_pre_df.Availability == False].index)
  test_pre_df = test_pre_df.drop(test_pre_df.columns[4], axis=1)
  test_pre_df.reset_index(drop = True,inplace = True)
  return test_pre_df
assertEquals(test_case_pre, population)

"""# CSV download"""

population_pre.to_csv('General population based on prefecture or state.csv',encoding='utf-8')
japan_pre_population.to_csv('Japan population based on prefecture or state.csv',encoding='utf-8')
usa_state_pop.to_csv('USA population based on prefecture or state.csv',encoding='utf-8')
malay_state_pop_df.to_csv('Malaysia population based on prefecture or state.csv',encoding='utf-8')
total.to_csv('Total population.csv',encoding='utf-8')