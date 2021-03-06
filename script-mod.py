from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
import requests
from time import sleep
'''
import os
import sqlite3
from fake_useragent import UserAgent
import shutil
from stem import Signal
from stem.control import Controller
import socket
import socks

controller = Controller.from_port(port=9051)
controller.authenticate()'''
req = requests.Session()
'''
def connectTor():
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5 , "127.0.0.1", 9050)
    socket.socket = socks.socksocket
def renew_tor():
    controller.signal(Signal.NEWNYM)
    
UA = UserAgent(fallback='Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2')
hdr = {'User-Agent': UA.random}'''
hdr = {'User-Agent': 'Mozilla/5.0'}

base_url = 'https://www.nstaffsstamps.uk/' 

def get_html(url):
    
    html_content = ''
    try:
        page = req.get(url, headers=hdr)
        html_content = BeautifulSoup(page.content, "html.parser")
    except: 
        pass
    
    return html_content

def get_details(url, selection):
    
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
        stamp['raw_text'] = raw_text.replace('"',"'")
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
        image_items = html.select('.main-image-container a')
        for image_item in image_items:
            img_href = image_item.get('href')
            if img_href != '#':
                img = 'https://www.nstaffsstamps.uk' + img_href
                if img not in images:
                    images.append(img)
    except:
        pass
    
    stamp['image_urls'] = images 
        
    # scrape date in format YYYY-MM-DD
    scrape_date = datetime.date.today().strftime('%Y-%m-%d')
    stamp['scrape_date'] = scrape_date
    
    stamp['url'] = url
    
    stamp['category']=selection
    
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

def get_category_page_items(page_url, selection):    
    while(page_url):
        page_items, page_url = get_page_items(page_url)
        for page_item in page_items:
            stamp = get_details(page_item, selection)
            '''if stamp['raw_text']==None and stamp['title']!=None:
                sleep(randint(1000,2000))
            next_step = query_for_previous(stamp)
            if next_step == 'continue':
                print('Only updating price')
                continue
            elif next_step == 'pass':
                print('Inserting the item')
                pass
            else:
                break
            db_update_image_download(stamp)'''
'''
def query_for_previous(stamp):
    # CHECKING IF Stamp IN DB
    os.chdir("/Volumes/Stamps/")
    conn1 = sqlite3.connect('Reference_data.db')
    c = conn1.cursor()
    col_nm = 'url'
    col_nm2 = 'raw_text'
    unique = stamp['url']
    unique2 = stamp['raw_text']
    c.execute('SELECT * FROM nstaffstamps WHERE {cn} == "{un}" AND {cn2} == "{un2}"'.\
                format(cn=col_nm, cn2=col_nm2, un=unique, un2=unique2))
    all_rows = c.fetchall()
    print(all_rows)
    conn1.close()
    price_update=[]
    price_update.append((stamp['url'],
    stamp['raw_text'],
    stamp['scrape_date'], 
    stamp['price'], 
    stamp['currency']))
    
    if len(all_rows) > 0:
        print ("This is in the database already")
        conn1 = sqlite3.connect('Reference_data.db')
        c = conn1.cursor()
        c.executemany("""INSERT INTO price_list (url, raw_text, scrape_date, price, currency) VALUES(?,?,?,?,?)""", price_update)
        conn1.commit()
        conn1.close()
        print (" ")
        #url_count(count)
        sleep(randint(45,75))
        next_step= 'continue'
        pass
    else:
        os.chdir("/Volumes/Stamps/")
        conn2 = sqlite3.connect('Reference_data.db')
        c2 = conn2.cursor()
        c2.executemany("""INSERT INTO price_list (url, raw_text, scrape_date, price, currency) VALUES(?,?,?,?,?)""", price_update)
        conn2.commit()
        conn2.close()
        next_step = 'pass'
    return(next_step)
    
def file_names(stamp):
    file_name = []
    rand_string = "RAND_"+str(randint(0,100000000))
    file_name = [rand_string+"-" + str(i) + ".png" for i in range(len(stamp['image_urls']))]
    return(file_name)
    
def db_update_image_download(stamp):  
    directory = "/Volumes/Stamps/stamps/nstaffsstamps/" + str(datetime.datetime.today().strftime('%Y-%m-%d')) +"/"
    image_paths = []
    file_name = file_names(stamp)
    image_paths = [directory + file_name[i] for i in range(len(file_name))]
    if not os.path.exists(directory):
        os.makedirs(directory)
    os.chdir(directory)
    for item in range(0,len(file_name)):
        print (stamp['image_urls'][item])
        try:
            imgRequest1=req.get(stamp['image_urls'][item],headers=hdr, timeout=120, stream=True)
        except:
            print ("waiting...")
            sleep(randint(3000,6000))
            print ("...")
            imgRequest1=req.get(stamp['image_urls'][item], headers=hdr, timeout=120, stream=True)
        if imgRequest1.status_code==200:
            with open(file_name[item],'wb') as localFile:
                imgRequest1.raw.decode_content = True
                shutil.copyfileobj(imgRequest1.raw, localFile)
                sleep(randint(25,40))
    stamp['image_paths']=", ".join(image_paths)
    database_update =[]
    # PUTTING NEW STAMPS IN DB
    database_update.append((
        stamp['url'],
        stamp['raw_text'],
        stamp['title'],
        stamp['scrape_date'],
        stamp['image_paths']))
    os.chdir("/Volumes/Stamps/")
    conn = sqlite3.connect('Reference_data.db')
    conn.text_factory = str
    cur = conn.cursor()
    cur.executemany("""INSERT INTO nstaffstamps ('url','raw_text', 'title', 
    'scrape_date','image_paths') 
    VALUES (?, ?, ?, ?, ?)""", database_update)
    conn.commit()
    conn.close()
    print ("++++++++++++")
    sleep(randint(80,160)) 
'''
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
        get_category_page_items(category, selection)
else:
    get_category_page_items(selected_main_category)
print('Scrape Complete!')
    
