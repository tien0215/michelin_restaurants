import requests
from bs4 import BeautifulSoup
import pandas as pd
import math
from pymongo import MongoClient
import certifi
import os
from dotenv import load_dotenv


# MongoDB connection
load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"),  tls=True ,tlsCAFile=certifi.where())
db = client.get_database('michelin_restaurant')  # Replace with your database name
collection = db.get_collection('restaurants')  # Replace with your collection name

# https://guide.michelin.com/en/tw/restaurants (Restaurant physically located in Taiwan.)
# https://guide.michelin.com/en/tw/restaurants/page/2
# https://guide.michelin.com/tw/zh_TW/restaurants (restaurant that related to Taiwan topic, usually more restaurant)
# https://guide.michelin.com/tw/zh_TW/restaurants/page/2?q=taiwan

# Set up the URL and headers
base_url="https://guide.michelin.com"
url = "https://guide.michelin.com/en/tw/restaurants"
index =0
restaurant_type= ["3-stars-michelin","2-stars-michelin","1-star-michelin","bib-gourmand","the-plate-michelin"]
for t in range(0,len(restaurant_type)):
    # Request the page content
    #response = requests.get(url, headers=headers)
    response = requests.get(url+"/"+restaurant_type[t])
    response.raise_for_status()  # Check for errors
    # Parse the page with BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    search_count_text = soup.find('div', class_='search-results__count').find('div', class_='search-results__stats').find('h1').get_text()
    search_count = search_count_text.split("of")[1].split(" ")[1].strip()

    if("," in search_count):
        search_count = search_count.replace(",", "")
    # Replace with the actual total count of results
    results_per_page = 20
    total_pages = math.ceil(int(search_count) / results_per_page)
    
    for page in range(1, total_pages + 1):
        # Update the URL with the current page number if pagination uses a "page" parameter
        if(page != 1): 
            page_url = f"{url}/{restaurant_type[t]}/page/{page}"
        else:
            page_url = url+"/"+restaurant_type[t] 
        
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
                restaurant_name = str(data.find('h1', class_='data-sheet__title').contents[0])
                restaurant_addr = str(data.find('div', class_='data-sheet__block--text').contents[0]).strip()
                restaurant_imgs = restaurant_page.find('div', class_='masthead__gallery-image').find_all('div', class_='masthead__gallery-image-item')
                restaurant_description = restaurant_page.find('div',class_='data-sheet__description').find('p')
                if(restaurant_description is None):
                    restaurant_description= restaurant_page.find('div',class_='data-sheet__description')
                img_arr = []
                for img in restaurant_imgs:
                    img_url = img.find('img').get('ci-src');
                    img_arr.append(img_url)
                restaurant_description = str(restaurant_description.contents[0]).strip()  
                restaurant_data = {
                "name": restaurant_name,
                "address": restaurant_addr,
                "image_url": img_arr,
                "michelin_type":restaurant_type[t],
                "comment":[],
                "description":restaurant_description
                }
                index +=1
                # Insert the data into MongoDB
                collection.insert_one(restaurant_data)
   
