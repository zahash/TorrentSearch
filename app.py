from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from scraper import search


app = Flask(__name__)

chrome_options = Options()
chrome_options.add_argument("--headless")

DRIVER = webdriver.Chrome("chromedriver", options=chrome_options)


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        query = request.form["query"]
        items = search(query, DRIVER)
        items = [vars(item) for item in items]
        return render_template("index.html", items=items)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(port=5000, debug=True)
