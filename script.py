from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
import requests
from time import sleep

base_url = 'https://www.nstaffsstamps.uk/' 

def get_html(url):
    
    html_content = ''
    try:
        page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        html_content = BeautifulSoup(page.content, "html.parser")
    except: 
        pass
    
    return html_content

def get_details(url):
    
    stamp = {}
    
    try:
        html = get_html(url)
    except:
        return stamp
    
    try:
        title = html.select('.prod-name')[0].get_text().strip()
        stamp['title'] = title
    except:
        stamp['title'] = None      
    
    try:
        raw_text_temp = html.select('#tab_desc')[0].get_text().strip()
        if 'If buying more than' in raw_text_temp:
            raw_text_parts = raw_text_temp.split('If buying more than')
            raw_text_temp = raw_text_parts[0]
        
        if 'ADDITIONAL CHECKOUT OPTIONS' in raw_text_temp:
            raw_text_parts = raw_text_temp.split('ADDITIONAL CHECKOUT OPTIONS')
            raw_text_temp = raw_text_parts[0]
            
        raw_text = raw_text_temp.strip() 
        stamp['raw_text'] = raw_text
    except:
        stamp['raw_text'] = None
    
    try:
        price = html.select('#_EKM_PRODUCTPRICE')[0].get_text().strip()
        stamp['price'] = price
    except:
        stamp['price'] = None  
        
    stamp['currency'] = 'GBP'
    
    # image_urls should be a list
    images = []                    
    try:
        image_items = html.select('.main-image a')
        for image_item in image_items:
            img = 'https://www.nstaffsstamps.uk' + image_item.get('href')
            if img not in images:
                images.append(img)
    except:
        pass
    
    stamp['image_urls'] = images 
        
    # scrape date in format YYYY-MM-DD
    scrape_date = datetime.date.today().strftime('%Y-%m-%d')
    stamp['scrape_date'] = scrape_date
    
    stamp['url'] = url
    
    print(stamp)
    print('+++++++++++++')
    sleep(randint(25, 65))
           
    return stamp

def get_page_items(url):
    
    items = []
    next_url = ''
    
    try:
        html = get_html(url)
    except:
        return items, next_url
    
    try:
        for item in html.select('.featured-product-name a'):
            item_link = base_url + item.get('href')
            if item_link not in items:
                items.append(item_link)
    except:
        pass
    
    try:
        next_item = html.find_all('link', attrs={'rel':'next'})[0]
        if next_item:
            next_url = base_url + next_item.get('href')
    except:
        pass   
    
    shuffle(list(set(items)))
    
    return items, next_url

def get_categories(url):
   
    items = []

    try:
        html = get_html(url)
    except:
        return items
    
    try:
        for item in html.select('.category-name a'):
            item_link = base_url + item.get('href')
            if item_link not in items: 
               items.append(item_link)
    except: 
        pass
    
    shuffle(list(set(items)))
    
    return items

def get_category_page_items(page_url):    
    while(page_url):
        page_items, page_url = get_page_items(page_url)
        for page_item in page_items:
            stamp = get_details(page_item) 

item_dict = {
"British Commonwealth": "https://www.nstaffsstamps.uk/british-commonwealth-8-c.asp",
"Foreign": "https://www.nstaffsstamps.uk/foreign-213-c.asp",
"Great Britain": "https://www.nstaffsstamps.uk/great-britain-227-c.asp",
"Thematics": "https://www.nstaffsstamps.uk/thematics-10-c.asp",
"Literature": "https://www.nstaffsstamps.uk/literature-418-c.asp",
"Miscellaneous": "https://www.nstaffsstamps.uk/miscellaneous-420-c.asp",
"Other": "https://www.nstaffsstamps.uk/other-440-c.asp"
    }
    
for key in item_dict:
    print(key + ': ' + item_dict[key])   

selection = input('Choose category: ')

selected_main_category = item_dict[selection]

categories = get_categories(selected_main_category) 
if len(categories):
    for category in categories:
        get_category_page_items(category)
else:
    get_category_page_items(selected_main_category)
    
