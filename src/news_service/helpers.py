import json
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup


def extract_url(url: str) -> str:
    return url.split("url=")[1].split("&")[0]


def parse_feed(url: str) -> list[str]:
    print(f"Fetching data from {url}")
    response = requests.get(url)
    if response.status_code == 200:
        text = response.text
        root = ET.fromstring(text)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", ns)
        urls = [entry.find("atom:link", ns).attrib["href"] for entry in entries]
        urls = [extract_url(url) for url in urls]
        return urls


def extract_contents(text: str) -> dict[str, str]:
    soup = BeautifulSoup(text, "html.parser")
    title = soup.find("h1").text.strip()
    paragraphs = soup.find_all("p")
    contents = "\n".join([p.text for p in paragraphs])
    json_data = {"title": title, "contents": contents}
    return json_data


def parse_news_urls(urls: list[str], folder: str):
    for i, url in enumerate(urls):
        print(f"Fetching and saving {url}")
        response = requests.get(url)
        if response.status_code == 200:
            try:
                text = response.text
                contents = extract_contents(text)
                return {"title": contents.title, "contents": contents.contents}
                # with open(f"{folder}/{i}.json", "w") as f:
                #     json.dump(title, f)
            except Exception as e:
                print(f"Failed to save {url}")
        else:
            print(f"Failed to fetch {url}")
    print(f"Saved {len(urls)} articles to {folder}")


def get_contents(): 


