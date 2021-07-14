from flask import Flask, render_template, redirect, Response, jsonify
from flask_pymongo import PyMongo
from bson import json_util
import json
import requests 
from bs4 import BeautifulSoup

# import sys, getopt, pprint
from flask_cors import CORS, cross_origin

# Create an instance of Flask
app = Flask(__name__, static_url_path='', static_folder='static')

CORS(app, resources={
    r"/*": {
        "origins": "*"
    }
})
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['CORS_ORIGINS'] = '*'
nutrition_dict = {}


app.config["MONGO_URI"] = "mongodb+srv://cooking-rec:Maura123$@emilo.z2rzr.mongodb.net/cooking-rec"
mongo = PyMongo(app)
cooking = mongo.db.cooking2
with open('data/csvjson.json') as f:
    data = json.load(f)
    for row in data:
        cooking.insert_one(row)
       
app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/nutritionfacts')
def NutritionFacts():
# @cross_origin()

    nutritionfacts = cooking.find_one()
    cookingjson = json.loads(json_util.dumps(nutritionfacts))

    return jsonify(cookingjson)

@app.route('/visualizations')
def visualizations():

    image_urls = {}
    response = requests.get("https://www.conceptdraw.com/examples/diagram-and-flowchart-related-to-nutritional-diet")

    food_pyramid_soup= BeautifulSoup(response.text,"html.parser")

    image_urls["food_pyramid_URL"]= food_pyramid_soup.find_all("img")[0]["src"]

    response = requests.get("https://www.businesswire.com/news/home/20180723005413/en/Global-Health-and-Wellness-Food-Market-2018-2022-Adoption-of-Healthy-Eating-Habits-to-Boost-Demand-Technavio")

    eating_habits_soup = BeautifulSoup(response.text,"html.parser")

    image_urls["eating_habits_image_URL"]= eating_habits_soup.find_all("img")[1]["src"]

    # alldb = cooking
    # nutritionfacts = alldb.find()
    # cookingjson = json.loads(json_util.dumps(nutritionfacts))

    return render_template('visualizations.html', images=image_urls)


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/products')
@app.route('/products/<search_term>')
def products(search_term="yogurt"):
    # products=requests.get(f"https://api.spoonacular.com/food/products/search?query={search_term}&apiKey=550da9ec7c8543adab2a7e0c47e20380").json()
    # recipes_products=products["products"]
    # searchTerm = 'papaya'
    # searchURL = f"https://www.wholefoodsmarket.com/search?text={searchTerm}"
    # response = requests.get(searchURL)
    # from pprint import pprint 
    # html_soup= BeautifulSoup(response.text,"html.parser")
    # pprint(html_soup)
    # int(html_soup.find("h1",class_="w-cms--font-headline__serif").text.split(" ")[1])
    # searchTerm = 'papaya'
    # searchURL = f"https://www.amazon.com/s?k={searchTerm}" 
    # searchTerm = 'papaya'
    whole_foods_URL= "https://www.wholefoodsmarket.com"
    searchURL = f"{whole_foods_URL}/search?text={search_term}"
    response = requests.get(searchURL)
    html_soup= BeautifulSoup(response.text,"html.parser")
    # int(html_soup.find("h1",class_="w-cms--font-headline__serif").text.split(" ")[1])
    product_suffix= html_soup.find("div","w-pie--products-grid").find("div", "w-pie--product-tile").find("a")["href"]
    product_URL = f"{whole_foods_URL}{product_suffix}"


    response = requests.get(product_URL)
    html_soup= BeautifulSoup(response.text,"html.parser")
    nutrition_facts_html = html_soup.find("section", "w-pie--nutrition-facts")#.find_all("div","nutrition-row")
    percent_divs = nutrition_facts_html.find_all("div", "nutrition-column text-bold text-right")
    label_divs= nutrition_facts_html.find_all("span", "text-indent")
    product_title=html_soup.find("h1", "w-cms--font-headline__serif").text
    product_image=html_soup.find("img", "iiz__img")["src"]



    nutrition_dict = {}
    nutrition_list=[]
    for i in range(0,len(percent_divs)):
        try:
            nutrition_product = {}
            nutrition_product["label"]= label_divs[i].text
            nutrition_product["percent"]= float(percent_divs[i].text.split("%")[0])
            nutrition_dict[f"{i}"]=nutrition_product
            nutrition_list.append({
                "label":label_divs[i].text,
                "percent":float(percent_divs[i].text.split("%")[0])
            })
        except: 
            pass
    cooking.update({},nutrition_dict,upsert=True)
    return render_template('products.html', recipes_products_list=nutrition_list, product_title=product_title, product_image=product_image)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':

    # Run this when running on LOCAL server...
    app.run(debug=True )

    # ...OR run this when PRODUCTION server.
    # app.run(debug=False)