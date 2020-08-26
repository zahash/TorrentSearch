import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Link:
    def __init__(self, url, country=None):
        self.url = url
        self.country = country

    def get_search_query_url(self, query):
        query = query.replace(" ", "+")
        return (
            "https://"
            + self.url
            + "/search.php?q="
            + query
            + "&all=on&search=Pirate+Search&page=0&orderby="
        )

    def __repr__(self):
        return "{}; {}".format(self.url, self.country)


class Item:
    def __init__(
        self,
        item_type,
        item_title,
        upload_date,
        magnet_link,
        item_size,
        seeders,
        leechers,
    ):
        self.item_type = item_type
        self.item_title = item_title
        self.upload_date = upload_date
        self.magent_link = magnet_link
        self.item_size = item_size
        self.seeders = seeders
        self.leechers = leechers

    def __repr__(self):
        return "Item(item_type={}, item_title={}, upload_date={}, magnet_link={}, item_size={}, seeders={}, leechers={})".format(
            self.item_type,
            self.item_title,
            self.upload_date,
            self.magent_link,
            self.item_size,
            self.seeders,
            self.leechers,
        )

    def __eq__(self, other):
        return self.magent_link == other.magent_link

    def __hash__(self):
        return self.magent_link.__hash__()


def get_proxy_site_urls():
    proxy_site_url = "https://piratebay-proxylist.net/"
    response = requests.get(proxy_site_url)
    html_page = response.content
    soup = BeautifulSoup(html_page, features="html.parser")

    url_links_table_body = soup.find("table", attrs={"class": "proxies"}).find("tbody")

    links = []
    for table_row in url_links_table_body.find_all("tr"):
        url = (
            table_row.find("td", attrs={"title": "URL"})
            .find("div", attrs={"class": "url-inner"})
            .find("span", attrs={"class": "domain"})
            .text.strip()
        )
        country = (
            table_row.find("td", attrs={"title": "Country"})
            .find("div", attrs={"class": "country"})
            .find("img", attrs={"class": "country-flag"})["title"]
            .strip()
        )

        links.append(Link(url=url, country=country))

    return links


def _extract_li_contents(list_element):
    item_type = ""
    item_type_span = list_element.find("span", attrs={"class": "list-item item-type"})
    for item_type_a in item_type_span.find_all("a"):
        item_type += item_type_a.text

    item_title = (
        list_element.find("span", attrs={"class": "list-item item-name item-title"})
        .find("a")
        .text
    )

    upload_date = list_element.find(
        "span", attrs={"class": "list-item item-uploaded"}
    ).text

    magnet_link = list_element.find("span", attrs={"class": "item-icons"}).find("a")[
        "href"
    ]

    item_size = list_element.find("span", attrs={"class": "list-item item-size"}).text

    seeders = list_element.find("span", attrs={"class": "list-item item-seed"}).text

    leechers = list_element.find("span", attrs={"class": "list-item item-leech"}).text

    item = Item(
        item_type=item_type,
        item_title=item_title,
        upload_date=upload_date,
        magnet_link=magnet_link,
        item_size=item_size,
        seeders=seeders,
        leechers=leechers,
    )

    return item


def scrape_results(url, driver):
    driver.get(url)
    content = driver.page_source
    soup = BeautifulSoup(content, features="html.parser")

    items = set()

    torrents_list = soup.find("ol", attrs={"id": "torrents"})

    # "list-entry alt"
    for list_element in torrents_list.find_all("li", attrs={"class": "list-entry"}):
        item = _extract_li_contents(list_element)
        items.add(item)

    for list_element in torrents_list.find_all("li", attrs={"class": "list-entry alt"}):
        item = _extract_li_contents(list_element)
        items.add(item)

    return list(items)


def search(query_string, driver):
    proxy_site_urls = get_proxy_site_urls()
    link = proxy_site_urls[0]

    items = scrape_results(link.get_search_query_url(query_string), driver)
    items = sorted(items, key=lambda x: x.seeders, reverse=True)

    return items


if __name__ == "__main__":

    chrome_options = Options()
    chrome_options.add_argument("--headless")

    driver = webdriver.Chrome("chromedriver", options=chrome_options)

    items = search("devil may cry 5", driver)
    for i in range(10):
        print(items[i])
        print("\n\n")
