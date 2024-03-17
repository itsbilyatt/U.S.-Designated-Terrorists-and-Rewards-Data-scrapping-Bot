########################################################################################################################
# creation history
########################################################################################################################
# created by prajyot birajdar
#work.prajyotbirajadar@gmail.com
########################################################################################################################
# import required modules
########################################################################################################################
import re
import json
import time
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from dateutil.parser import parse
import pandas as pd


########################################################################################################################
# gat_response function
########################################################################################################################
def get_response(url):
    soup = ''
    for i in range(3):
        try:
            print(f'Processing url it will give you soup object {url}')
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            driver = webdriver.Chrome(options=options)
            driver.get(url)
            time.sleep(20)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source,'html.parser')
            break
        except Exception as e:
            print(f'Not getting soup object retrying{url}')
    return soup


#######################################################################################################################
# function to get max_page
#######################################################################################################################
def max_pages():
    url = "https://rewardsforjustice.net/index/"
    soup = get_response(url)
    max_pages = soup.find('div',class_='jet-smart-filters-pagination jet-filter').find_all_next('div')[9].text
    return max_pages


########################################################################################################################
#  function to get all pages
########################################################################################################################
def collect_info_urls(soup):
    list_urls = []
    category_data = []
    info_urls = soup.findAll('a', re.compile(r'jet-engine-listing-overlay-link'))
    for info_url in info_urls:
        url_tag = info_url.get('href')
        list_urls.append(url_tag)

    category_list = soup.find_all('div',class_ = "elementor-column elementor-col-100 elementor-inner-column elementor-element elementor-element-04fa3df")
    for category_tag in category_list:
        category_tag = category_tag.find_all_next('div')[2].text
        category_data.append(category_tag.replace(r'\n',''))
    print(f'list urls and category_list are collected succefully')
    return list_urls,category_data


########################################################################################################################
#  function to get all data from each page
########################################################################################################################
def extract_data_from_each_url():

    Page_url,Category,Title ,Reward_amount,Associated_organization,Associated_location,About,Image_url,Date_birth = [],[],[],[],[],[],[],[],[]
    details_url,category,title,image_list,reward_amount,associated_organization,associated_location,date_of_birth,about = 'null','null','null','null','null','null','null','null','null'

    for page_no in range(1, int(max_pages())+1):
    # for page_no in range(1, 3):
    #     index_url = "https://rewardsforjustice.net/index/?jsf=jet-engine:rewards-grid&tax=crime-category:1070%2C1071%2C1073%2C1072%2C1074&pagenum={}".format(str(page_no))
        index_url = "https://rewardsforjustice.net/index/?jsf=jet-engine:rewards-grid&tax=crime-category:1070%2C1071%2C1073%2C1072%2C1074&pagenum={}".format(str(page_no))
        soup_data = get_response(index_url)
        list_urls, category_list = collect_info_urls(soup_data)
        for details_url,category in zip(list_urls,category_list):
            title = details_url.split(r'/')[-2].upper()
            image_list = []
            Page_url.append(details_url)
            Category.append(category)
            Title.append(title)
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')

            driver = webdriver.Chrome(options=options)
            driver.get(details_url)
            time.sleep(3)
            page_source = driver.page_source
            soup = BeautifulSoup(page_source,'html.parser')

            image_tags = soup.find_all('div', id='gallery-1')
            for image_tag in image_tags:
                image_list.append(image_tag.findChild('a').get('href'))

            Image_url.append(image_list)

            reward_tag = soup.find('div', id='reward-box').find_all_next('div')[3]
            reward_amount = reward_tag.text
            Reward_amount.append(reward_amount)

            about_tag = soup.find('div', class_ = "elementor-column elementor-col-50 elementor-top-column elementor-element elementor-element-93ad9a9").find_all_next('div')
            associated_organization = about_tag[55].text
            Associated_organization.append(associated_organization)
            associated_location = about_tag[20].text
            Associated_location.append(associated_location)



            date_of_birth = about_tag[30].text
            try:
                date_of_birth = parse(date_of_birth)
                date_of_birth = date_of_birth.strftime("%Y-%m-%d")
                Date_birth.append(date_of_birth)
            except:
                Date_birth.append('null')

            about_info_tag = soup.find('div', class_ = "elementor-element elementor-element-52b1d20 elementor-widget elementor-widget-theme-post-content")
            about = about_info_tag.text
            About.append(about)

    keys = ["Page_url", "Category", "Title", "Reward_amount", "Associated_organization", "Associated_location", "About",
            "Image_url", "Date_birth"]
    values = [Page_url, Category, Title, Reward_amount, Associated_organization, Associated_location, About, Image_url,
              Date_birth]
    data = dict(zip(keys, values))
    print(data)
    return data

########################################################################################################################
#  function to save data
########################################################################################################################
def save_data():
    data = extract_data_from_each_url()
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y%m%d_%H%M%S")
    file_name = 'PRAWSB_' + formatted_datetime + '.json'
    with open(file_name, 'w') as f:
        json.dump(data, f)
    print('Json File is saved successfully')
    file_name_xl = 'PRAWSB_' + formatted_datetime + '.xlsx'
    df = pd.DataFrame(data)
    df.to_excel(file_name_xl, index=False)
    print('excel file is created successfully')

save_data()
########################################################################################################################
#  END of collection
########################################################################################################################
