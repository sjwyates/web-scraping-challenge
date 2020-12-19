from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
from .scrape_mars import scrape_info


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/weather_app"
mongo = PyMongo(app)


@app.route("/")
def home():
    mars_data = mongo.db.mars_data.find_one()
    return render_template("index.html", mars_data=mars_data)


@app.route("/scrape")
def scraper():
    mars_data = mongo.db.mars_data
    scraped_data = scrape_info()
    mars_data.update({}, scraped_data, upsert=True)
    return redirect("/", code=302)


if __name__ == "__main__":
    app.run(debug=True)