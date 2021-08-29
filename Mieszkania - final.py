#!/usr/bin/env python
# coding: utf-8

# In[69]:


import requests, re, numpy
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt
from unidecode import unidecode
from datetime import date

####################### PROBLEM - REGEX W DZIELNICACH NIE ROZPOZNAJE DZIELNIC Z KROPKĄ ########################

def getInfo(url):
    r = requests.get(url)
    if r.status_code != 200:
        raise ValueError
    else:
        soup = BeautifulSoup(r.text, 'html.parser')
    return soup

df_cities = pd.read_csv('pl.csv', header = None)
df_cities.columns = df_cities.iloc[0]
df_cities = df_cities.drop(df_cities.index[0])
df_cities_list = list(df_cities['city'])
df_cities_list.append('Warszawa')

while True:
    query_type = input('\nPlease type in if you are looking for apartments for sale or rentals\n')
    if query_type.lower() in ['sprzedaz', 'sprzedaż', 'wynajem', 'najem']:
        break
while True:
    city = input('\nPlease type in your city\n')   #City input for the main function
    if city.capitalize() in df_cities_list:
        break
        
city_improved = city.replace('ń', 'n').replace('ł', 'l').replace('ą', 'a').replace('ę', 'e').replace('ć', 'c').replace('ó', 'o').replace('ś', 's').replace('ż', 'z').replace('ź', 'z')

def getEverything():   #Main scraping function
    global city_improved
    pages = []
    page = 1
    if query_type.lower() == 'wynajem' or query_type.lower() == 'najem':
        while True:
            try:
                all_data = getInfo(f'https://www.otodom.pl/pl/oferty/wynajem/mieszkanie/{city_improved.lower()}?page={page}')
                apartments = all_data.find_all('ul', class_ = 'css-14cy79a e3x1uf06')
                if all_data.find('h3', class_ = 'css-1b2au34 e1qwpsp42'):
                    break
                else:
                    for i in apartments:
                        if apartments.index(i) % 2 == 1:
                            pages.append(i)
                page += 1
            except ValueError:
                break
    else:
        while True:
            try:
                all_data = getInfo(f'https://www.otodom.pl/pl/oferty/sprzedaz/mieszkanie/{city_improved.lower()}?market=PRIMARY&page={page}&limit=24')
                apartments = all_data.find_all('ul', class_ = 'css-14cy79a e3x1uf06')
                if all_data.find('h3', class_ = 'css-1b2au34 e1qwpsp42'):
                    break
                else:
                    for i in apartments:
                        if apartments.index(i) % 2 == 1:
                            pages.append(i)
                page += 1
            except ValueError:
                break
        
    return pages
    

var = getEverything()   #Running the main function here

def getTitle():
    arr = []
    for i in var:
        for x in i:
            if x.find('h3', class_ = 'css-1873em4 es62z2j25') != None:
                arr.append(x.find('h3', class_ = 'css-1873em4 es62z2j25').text.strip())
            else:
                pass 
    return arr

def getRooms():  
    arr = []
    for i in var:
        for x in i:
            if x.find('span', class_ = 'css-348r18 es62z2j21') != None:
                arr.append(int(x.find('span', class_ = 'css-348r18 es62z2j21').text[0]))
            else:
                pass
    return arr

def getSurface():   
    arr = []
    surface = []
    for i in var:
        for x in i:
            if x.find('p', class_ = 'css-xlgkh5 es62z2j22') != None:
                arr.append(x.find('p', class_ = 'css-xlgkh5 es62z2j22'))
            else:
                pass
    for x in arr:
        for i in x:
            if x.index(i) == 1:
                surface.append(i.text.strip())
                
    surface_regex = re.compile(r'\d+(\W\d+)?')
    surfaces_regex = []
    for i in surface:
        mo = surface_regex.search(i)
        surfaces_regex.append(mo.group().strip())

    surfaces_regex = [float(x) + 0.00001 for x in surfaces_regex]


    return surfaces_regex

def getOfferOwner():   
    arr = []
    arr_2 = []
    for i in var:
        for x in i:
            if x.find('p', class_ = 'css-1cmayta es62z2j13') != None:
                arr.append(x.find('p', class_ = 'css-1cmayta es62z2j13').text.strip())
    for i in arr:
        if query_type.lower() in ['sprzedaz', 'sprzedaż']:
            if 'Inwestycja deweloperska' in i:
                i = i.replace('Inwestycja deweloperska', '')
                arr_2.append(i)
            elif 'Biuro nieruchomości' in i and 'Inwestycja deweloperska' not in i:
                i = i.replace('Biuro nieruchomości', '')
                arr_2.append(i)
            else:
                arr_2.append('Oferta prywatna')
        else:
            if 'Biuro nieruchomości' in i and 'Biuro nieruchomości ' not in i and ' Biuro nieruchomości' not in i:
                i = i.replace('Biuro nieruchomości', '')
                arr_2.append(i)
            elif 'Inwestycja deweloperska' in i:
                i = i.replace('Inwestycja deweloperska', '')
                arr_2.append(i)
            else:
                arr_2.append('Oferta prywatna')
    arr_2 = ['N/A' if x == '' else x for x in arr_2]
    return arr_2

def getListingCategory():   
    arr = []
    arr_2 = []
    for i in var:
        for x in i:
            if x.find('p', class_ = 'css-1cmayta es62z2j13') != None:
                arr.append(x.find('p', class_ = 'css-1cmayta es62z2j13').text.strip())
    for i in arr:
        if query_type.lower() in ['wynajem', 'najem']:
            if 'Biuro nieruchomości' in i:
                arr_2.append('Biuro nieruchomości')
            else:
                arr_2.append('Oferta prywatna')
        else:
            if 'Inwestycja deweloperska' in i:
                arr_2.append('Inwestycja deweloperska')
            elif 'Oferta prywatna' in i:
                arr_2.append('Oferta prywatna')
            else:
                arr_2.append('Biuro nieruchomości')
    return arr_2

def getPrice():
    arr = []
    prices = []
    floates = []
    for i in var:
        for x in i:
            if x.find('p', class_ = 'css-lk61n3 es62z2j20') != None:
                arr.append(unidecode(x.find('p', class_ = 'css-lk61n3 es62z2j20').text))
            elif x.find('p', class_ = 'css-5kmdsl es62z2j20') != None:
                arr.append(unidecode(x.find('p', class_ = 'css-5kmdsl es62z2j20').text))
            else:
                pass
    prices_regex = re.compile(r'\d+(\ \d+)?(\ \d+)?(\,\d+)?')
    for x in arr:
        if 'Zapytaj' not in x:
            mo = prices_regex.search(x)
            prices.append(mo.group())
        else:
            prices.append('N/A')
    for x in prices:
        try:
            x = x.replace(',', '.').replace(' ', '')
            x = float(x) + 0.001
            floates.append(x)
        except:
            floates.append(x)
            
    return floates  

def getPricePerSquareMeter():
    arr = []
    prices = []
    floates = []
    for i in var:
        for x in i:
            if x.find('p', class_ = 'css-xlgkh5 es62z2j22') != None:
                arr.append(x.find('p', class_ = 'css-xlgkh5 es62z2j22'))
            else:
                pass
    for x in arr:
        for i in x:
            if x.index(i) == 2:
                    prices.append(unidecode(i.text.strip()))
                    
    prices_regex = re.compile(r'\d+(\ \d+)?(\ \d+)?(\,\d+)?')
    
    for x in prices:
        if x != '':
            mo = prices_regex.search(x)
            floates.append(float(mo.group().replace(' ', '').replace(',', '.')) + 0.001)
        else:
            floates.append('N/A')                 
                    
                    
                    
    return floates

def getNH():
    global city
    arr = []
    for i in var:
        for x in i:
            if x.find('span', class_ = 'css-17o293g es62z2j23') != None:
                arr.append(x.find('span', class_ = 'css-17o293g es62z2j23').text.strip())
            else:
                pass
    nh_regexed = []        
    nh_regex = re.compile(r'\,\ \w+(\.\ \w+)?(\.\w+)?(\ \w+)?')
    for i in arr:
        mo = nh_regex.search(i)
        nh_regexed.append(mo.group().strip()[2::])
    errors = ['mazowieckie', 'kujawsko', 'wielkopolskie', 'zachodnio', 'zachodniopomorskie', 'pomorskie', 'małopolskie', 'świętokrzyskie',
             'podlaskie', 'warmińsko', 'śląskie', 'opolskie', 'łódzkie', 'podkarpackie', 'dolnośląskie']
    
    nh_regexed = [x if x not in errors else 'N/A' for x in nh_regexed]      
    nh_regexed = [x if x != city.capitalize() else 'N/A' for x in nh_regexed]  
            
            
            
    return nh_regexed

def getOfferLink():
    arr = []
    arr_2 = []
    for i in var:
        for x in i:
            if x.find('a', class_ = 'css-19ukcmm es62z2j29') != None:
                arr.append('https://www.otodom.pl' + x.find('a', class_ = 'css-19ukcmm es62z2j29')['href'])
    return arr


# In[70]:


len(getNH()), len(getSurface()), len(getOfferLink()), len(getPrice()),len(getListingCategory()), len(getOfferOwner()), len(getRooms()), len(getTitle()), len(getPricePerSquareMeter())


# In[71]:


if query_type.lower() in ['sprzedaz', 'sprzedaż']:
    df = pd.DataFrame({'Offer name':getTitle(), 'Offer owner' : getOfferOwner(), 'Listing category' : getListingCategory(), 'Surface' : getSurface(), 'Number of rooms' : getRooms(), 'Price of the property' : getPrice(), 'Price per square meter': getPricePerSquareMeter(), 'Neighborhood' : getNH(), 'Offer link' : getOfferLink()})
else:
    df = pd.DataFrame({'Offer name':getTitle(), 'Offer owner' : getOfferOwner(), 'Listing category' : getListingCategory(), 'Surface' : getSurface(), 'Number of rooms' : getRooms(), 'Rent per month' : getPrice(), 'Neighborhood' : getNH(), 'Offer link' : getOfferLink()})


# In[72]:


df


# In[68]:


now = datetime.now()   #setting actual date and time as a variable
dt_string = now.strftime("%d-%m-%Y %H:%M:%S")
df.to_csv(f'{city.capitalize()} {dt_string}.csv', encoding='utf-8', index = False)   #Saving DataFrame as CSV


# In[74]:


if query_type.lower() in ['wynajem', 'najem']:
    df_grouped_price = df.groupby('Neighborhood')['Price per month'].mean()   #Works only for rentals
df_grouped_rooms = df.groupby('Neighborhood')['Number of rooms'].mean()
df_grouped_count = df.groupby('Neighborhood')['Number of rooms'].count()
df_grouped_surface = df.groupby('Neighborhood')['Surface'].mean()
df_grouped_listing_count = df.groupby('Neighborhood')['Listing category'].count()


# In[ ]:


new_df = df[['Neighborhood', 'Listing category']].groupby(['Neighborhood', 'Listing category']).size()
new_df_arr = []
new_df_arr_to_drop = []
new_df = dict(new_df)
new_df_keys = list(new_df.keys())
for i in new_df_keys:
    new_df_arr.append(i[0])
for i in new_df_arr:
    if new_df_arr.count(i) < 2:
        new_df_arr_to_drop.append(i)
        
df_improved = df[~df['Neighborhood'].isin(new_df_arr_to_drop)]


# In[ ]:


df.sort_values(by = 'Price per month')   #Works only for rentals


# In[ ]:


df_loc_private_offers = df_improved.loc[df['Listing category'] == 'Oferta prywatna']
del df_loc_private_offers['Offer name']
del df_loc_private_offers['Offer owner']
del df_loc_private_offers['Surface']
del df_loc_private_offers['Number of rooms']
del df_loc_private_offers['Price per month']
del df_loc_private_offers['Offer link']
df_loc_private_offers_groupby = df_loc_private_offers.groupby('Neighborhood')['Listing category'].count()
df_loc_brokerage_offers = df_improved.loc[df['Listing category'] == 'Biuro nieruchomości']
del df_loc_brokerage_offers['Offer name']
del df_loc_brokerage_offers['Offer owner']
del df_loc_brokerage_offers['Surface']
del df_loc_brokerage_offers['Number of rooms']
del df_loc_brokerage_offers['Price per month']
del df_loc_brokerage_offers['Offer link']
df_loc_brokerage_offers.columns = ['Listing category 2', 'Neighborhood']
df_loc_brokerage_offers_groupby = df_loc_brokerage_offers.groupby('Neighborhood')['Listing category 2'].count()
groups_private = dict(df_loc_private_offers_groupby)
groups_broker = dict(df_loc_brokerage_offers_groupby)
ds = [groups_private, groups_broker]
d = {}


# In[ ]:


for k in groups_private.keys():
    d[k] = tuple(d[k] for d in ds)
connected_arr = []
keys = list(d.keys())
values = list(d.values())
for x, y in zip(keys, values):
    connected_arr.append([x, y[0], y[1]])
df_listing_category = pd.DataFrame(connected_arr)
df_listing_category.columns = ['Neighborhood', 'Private', 'Broker']
df_listing_category = df_listing_category.set_index('Neighborhood')
df_listing_category.plot.bar(figsize = (20, 8))
plt.grid()
plt.savefig(f'{city.capitalize()} - Liczba różnych rodzajów ofert w zależności od dzielnicy')


# In[ ]:


df_grouped_price.plot.bar(figsize = (20, 8))
plt.grid()
plt.savefig(f'{city.capitalize()} - ceny na osiedle')


# In[75]:


df_grouped_count.plot.bar(figsize = (20,8))
plt.grid()
plt.savefig(f'{city.capitalize()} - ilość mieszkań na osiedle')


# In[ ]:


df_grouped_rooms.plot.bar(figsize = (20,8))
plt.grid()
plt.savefig(f'{city.capitalize()} - średnia ilość pokoi na osiedle')


# In[ ]:


df_grouped_surface.plot.bar(figsize = (20,8))
plt.grid()
plt.savefig(f'{city.capitalize()} - średnia wielkość mieszkania na osiedlu')


# In[ ]:





# In[ ]:




