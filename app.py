from flask import Flask, render_template, redirect
import pymongo
from bs4 import BeautifulSoup
import pandas as pd
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager
import time
import scrape_mars

app=Flask(__name__)


mongo_conn='mongodb://localhost:27017'
client=pymongo.MongoClient(mongo_conn)

@app.route('/')
def index():
    data_from_mongo=client.mars_db.mars.find_one()
    return render_template('index.html', data_from_flask=data_from_mongo)

@app.route('/scrape')
def scrape():
    mars = client.mars_db.mars
    mars_data = scrape_mars.scrape()
    mars.update({}, mars_data, upsert=True)
    return redirect("/", code=302)

if __name__=='__main__':
    app.run(debug=True)
