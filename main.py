import requests
from pprint import pprint
from html.parser import HTMLParser
from collections import defaultdict
import json
import re
import csv
import selenium.webdriver
from selenium.webdriver.common.by import By
from datetime import datetime

URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTYcli77i_Q8vR0zUyWOWO1J0so4Uq2w2tqXDIXDim6HMD9SDDUqVdtjRvywEPfDl2L2F5oWMVLA8ZV/pub?gid=451128911&single=true&output=tsv";

class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = defaultdict(dict)
        self.metas = {}
        self.published = None

    def handle_starttag(self, tag, attrs):
        if tag != "meta":
            return

        attrs = dict(attrs)

        try:
            if attrs["property"] in ["article:published_time", "og:article:published_time"]:
                self.published = attrs["content"]
                return

            if not attrs["property"].startswith("og:"):
                return

            if attrs["property"] == "og:image":
                hid = attrs.get("data-hid") or "default"
                self.images[hid]["src"] = attrs["content"]
            elif attrs["property"] == "og:image:height":
                hid = attrs.get("data-hid") or "default"
                hid = hid.removesuffix("-height")
                self.images[hid]["height"] = int(attrs["content"])
            elif attrs["property"] == "og:image:width":
                hid = attrs.get("data-hid") or "default"
                hid = hid.removesuffix("-width")
                self.images[hid]["width"] = int(attrs["content"])
            else:
                self.metas[attrs["property"]] = attrs["content"]
        except:
            pass

def main():
    driver = selenium.webdriver.Firefox()
    response = requests.get(URL)

    # For some reason, requests thinks its ISO-8859-1, but it is actually UTF-8
    text = response.content.decode("UTF-8")

    reader = csv.DictReader(text.split("\n"), dialect="excel-tab")

    data = []

    for line in reader:
        new_data = {}

        for key, value in line.items():
            new_data[key.lower().strip()] = value
    
        try:
            page_response = requests.get(new_data["url"])
            text = page_response.text

            parser = MyHTMLParser()
            parser.feed(text)

            # Remove some tracking info and stuff
            if "og:url" in parser.metas:
                new_data["url"] = parser.metas["og:url"]
                
            if parser.published:
                new_data["published"] = parser.published
            else:
                # Bring out the big guns for Instagram
                # We scrape all the time elements, which are present on both
                # posts and comments. We assume that the time of the post is
                # the oldest because all the comments must be made after the
                # post.
                print(f"Selenium for {new_data["url"]}")
                driver.get(new_data["url"])
                timestamps = driver.find_elements(By.XPATH, "//time")

                timestamps = list(map(lambda t: t.get_attribute('datetime'), timestamps))

                new_data["published"] = min(
                    timestamps,
                    key = lambda t: datetime.fromisoformat(t.replace('Z', '+00:00')),
                )

            new_data["metas"] = parser.metas
            new_data["images"] = parser.images
        except Exception as e:
            print(e)
            continue

        data.append(new_data)

    data.sort(reverse = True, key = lambda x: datetime.fromisoformat(x["published"]))

    with open("articles.json", "w") as f:
        json.dump(data, f, indent = 2)

def has_attr(el, attr):
    try:
        el.get_attribute('datetime')
        return True
    except:
        return False

if __name__ == "__main__":
    main()
