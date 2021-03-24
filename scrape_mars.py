
from bs4 import BeautifulSoup
import pandas as pd
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager
import time
import pymongo
import requests

"""
# NASA Mars News
"""
def scrape():

    nasa_url='https://mars.nasa.gov/news'

    #collect latest News Title and Paragraph Text

    #Create a driver
    executable_path={'executable_path': ChromeDriverManager().install()}
    browser=Browser('chrome', **executable_path, headless=False)

    browser.visit(nasa_url)
    time.sleep(1)
    html=browser.html

    soup=BeautifulSoup(html, 'html.parser')

    #use bs4 to parse out the title and paragraph
    news_t=soup.find('div', class_='bottom_gradient').text
    news_p=soup.find('div', class_='article_teaser_body').text


    """
    # JPL Mars Space Images - Featured Image
    """

    #Image addresses

    #Switching gears and looking for images at path provided by instructions
    nasa_image_url='https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(nasa_image_url)

    html=browser.html

    #find the image thumbnail and click on it, then grab the html at the new page to go to next page
    browser.find_by_css('.BaseImage').click()
    time.sleep(1)
    html=browser.html
    soup=BeautifulSoup(html, 'html.parser')

    image_tag=soup.find('a', class_='BaseButton text-contrast-none w-full mb-5 -primary -compact inline-block')
    image_url=image_tag['href']


    """
    # Mars Facts
    """

    # Use pandas module to get html; scrape the table into a list of df object
    table_path='https://space-facts.com/mars/'
    tables = pd.read_html(table_path)


    #Use the pandas method to convert a df to html string
    #Parse out only specific table data required
    tables_df=tables[2]
    table_html=tables_df.to_html(index=False, header=None)

    """
    # Mars Hemispheres
    """

    # Obtain full resolution image urls for each of Mars' hemispheres
    usgs_url='https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(usgs_url)

    #Allow the browser time to load after switching pages
    time.sleep(1)
    html=browser.html
    soup=BeautifulSoup(html, 'html.parser')

    #Create a list to hold the hemisphere dictionaries
    hemisphere_image_urls=[]

    #Look for results in soup
    results=soup.find_all('div', class_='item')

    for result in results:
        try:
    #Save the Hemisphere title
            title = result.h3.text
    #Click on the URL and obtain image url for full-resolution image:
            url=result.find('a')['href']
            full_url='https://astrogeology.usgs.gov'+url
            browser.visit(full_url)
            img_url=browser.find_by_text('Sample')['href']
        except:
            img_url=''
            title='Image Not Found'
    # Append the dictionary with the image url string and the hemisphere title to a list. 
    # This list will contain one dictionary for each hemisphere.
        hemisphere_image_dict={'Title': title,
                                'Image URL': img_url}
        hemisphere_image_urls.append(hemisphere_image_dict)

        browser.quit()

    #mongo connection string 
    mongo_conn='mongodb://localhost:27017'
    client=pymongo.MongoClient(mongo_conn)

    insert_data={'news_t': news_t,
                'news_p': news_p,
                'image_url': image_url,
                'table_html': table_html,
                'hemisphere_images': hemisphere_image_urls}

    client.mars_db.mars.replace_one({},insert_data, upsert=True)

    return insert_data