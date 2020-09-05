import argparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scraper import search


ap = argparse.ArgumentParser(allow_abbrev=False)
ap.add_argument(
    "-q",
    "--query",
    default="",
    type=str,
    help="Search Query",
)


args = ap.parse_args()


if __name__ == "__main__":

    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome("chromedriver", options=chrome_options)

    items = search(args.query, driver)
    for item_num, item in enumerate(items):
        print("{}.".format(item_num+1))
        print(item)
        print("\n\n")
