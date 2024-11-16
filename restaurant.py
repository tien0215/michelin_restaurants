import requests
from bs4 import BeautifulSoup
import pandas as pd
import math
from pymongo import MongoClient
import certifi
import os

# MongoDB connection
client = MongoClient(os.getenv("MONGODB_URI"),  tls=True ,tlsCAFile=certifi.where())
db = client.get_database('michelin_restaurant')  # Replace with your database name
collection = db.get_collection('restaurants')  # Replace with your collection name

# Set up the URL and headers
base_url="https://guide.michelin.com"
url = "https://guide.michelin.com/tw/zh_TW/restaurants"

restaurant_type= ["3-stars-michelin","2-stars-michelin","1-star-michelin","bib-gourmand","the-plate-michelin"]
for t in range(0,len(restaurant_type)):
    print(url+"/"+restaurant_type[t]+"?q=taiwan")
    # Request the page content
    #response = requests.get(url, headers=headers)
    response = requests.get(url+"/"+restaurant_type[t]+"?q=taiwan")
    response.raise_for_status()  # Check for errors
    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    search_count_text = soup.find('div', class_='search-results__count').find('div', class_='search-results__stats').find('h1').get_text()
    search_count = search_count_text.split("共")[1].split("個")[0].strip()
    if("," in search_count):
        search_count = search_count.replace(",", "")
    # Replace with the actual total count of results
    print(search_count)
    results_per_page = 20
    total_pages = math.ceil(int(search_count) / results_per_page)

    for page in range(1, total_pages + 1):
        # Update the URL with the current page number if pagination uses a "page" parameter
        if(page != 1): 
            page_url = f"{url}/{restaurant_type[t]}/page/{page}?q=taiwan"
        else:
            page_url = url+"/"+restaurant_type[t]+"?q=taiwan" 
        '''
        # Request the page content
        response = requests.get(page_url)
        response.raise_for_status()  # Check for errors
    
        # Parse the page with BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the main restaurant container for this page
        restaurant_column = soup.find('div', class_='search-results__column')

        if restaurant_column:
            # Find all individual restaurant rows within the column
            restaurant_rows = restaurant_column.find('div', class_='row restaurant__list-row js-restaurant__list_items')
            restaurant_list = restaurant_rows.find_all('div', class_='col-md-6 col-lg-4 col-xl-3')
        
            # Write each restaurant's HTML content to the file
            for r in restaurant_list:
                item = r.find('div', class_='js-restaurant__list_item').find('div', class_='card__menu-image').find('a')
                restaurant_url= base_url+item.get('href')
                restaurant_page_response= requests.get(restaurant_url)
                restaurant_page_response.raise_for_status()
                restaurant_page = BeautifulSoup(restaurant_page_response.text, 'html.parser')
                data = restaurant_page.find('div', class_='restaurant-details').find('section', class_='section section-main d-block d-lg-none').find('div', class_='data-sheet')
                restaurant_name = str(data.find('h1', class_='data-sheet__title').contents[0]);
                restaurant_addr = str(data.find('div', class_='data-sheet__block--text').contents[0]).strip()
                restautrant_img = str(restaurant_page.find('div', class_='masthead__gallery-image').get('data-bg'))
                restaurant_data = {
                "name": restaurant_name,
                "address": restaurant_addr,
                "image_url": restautrant_img,
                "michelin_type":restaurant_type[t],
                "description":""
                }
                # Insert the data into MongoDB
                #collection.insert_one(restaurant_data)
                '''
