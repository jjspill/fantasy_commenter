import hashlib
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup
from google.cloud import firestore
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from player_context import player_context as PLAYER_CONTEXT

db = firestore.Client()


# Generate a SHA-256 hash of a URL to use as a Firestore document ID.
def hash_url(url: str) -> str:
    hash_object = hashlib.sha256()
    hash_object.update(url.encode("utf-8"))
    return hash_object.hexdigest()


# Add a new URL to the Firestore database with a processed status
def add_url_to_db(url):
    hash = hash_url(url)
    url_ref = db.collection("processed_urls").document(hash)
    url_ref.set({"url": url, "processed": True})


# Check if a URL has already been processed
def check_if_url_processed(url):
    hash = hash_url(url)
    url_ref = db.collection("processed_urls").document(hash)
    doc = url_ref.get()
    if doc.exists:
        return True
    else:
        return False


def extract_url(url: str) -> str:
    return url.split("url=")[1].split("&")[0]


# Parse RSS feed and extract URLs
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


# Fetch news URLs and parse contents
def parse_news_urls(urls: list[str]):
    for i, url in enumerate(urls):
        if check_if_url_processed(url):
            print(f"URL {url} has already been processed")
            continue

        add_url_to_db(url)
        response = requests.get(url)
        if response.status_code == 200:
            try:
                text = response.text
                contents = extract_contents(text)
                yield contents

            except Exception as e:
                print(f"Error extracting {url}: {e}")
                continue
        else:
            print(f"Error fetching {url}: {response.status_code}")
            continue


# Parse contents
def extract_contents(text: str) -> dict[str, str]:
    soup = BeautifulSoup(text, "html.parser")
    title = soup.find("h1").text.strip()
    paragraphs = soup.find_all("p")
    contents = "\n".join(p.text.strip() for p in paragraphs)
    return {"title": title, "contents": contents}


# Parse the llm output and organize the player information
def parse_player_info(player_info):
    player_infos = player_info.split("\n\n")

    for player_info in player_infos:
        lines = player_info.split("\n")
        player_header = lines[0]
        header_parts = player_header.split()
        if len(header_parts) < 3:
            continue
        player_name = " ".join(header_parts[1:-2]).strip()
        team_position = header_parts[-2:]
        team = team_position[0]
        position = team_position[1].replace(":", "")
        print(player_name, team, position)

        info_list = lines[1:]
        player_dict = {
            "name": player_name,
            "team": team,
            "position": position,
            "info": info_list,
        }
        return player_dict


# Extract player information from the article
def extract_player_info(title: str, contents: str) -> str:
    if "baseball" in title.lower():
        return
    context = f"Title: {title}\n\nContents: {contents}"
    messages = [
        SystemMessage(
            content=f"You are a fantasy football expert and you are reading articles about fantasy football trying to get an edge on your competition. For each player in the article provided: 1. List the name of the player followed by a colon, then for each new thing learned about the player list them starting with 1. You want to write productive notes so that one can easily evaluate the player in the future. MAKE SURE TO ORGANIZE YOUR RESPONSE BY PLAYER NAME FOR EASY RETRIEVAL. EVERY TIME NEW A PLAYER IS MENTIONED MAKE SURE TO START A NEW LINE WITH `PLAYER: [PLAYER FULL NAME] [PLAYER TEAM] [PLAYER POSITION]` FOLLOWED BY A COLON.IF ONE PIECE OF INFORMATION TALKS ABOUT TWO PLAYERS, MAKE SURE TO LIST THE INFORMATION UNDER BOTH PLAYERS. If you are unable to find any information about a player, don't include them in the output. USE THIS LIST TO FIND PLAYERS TEAMS AND POSITIONS: {PLAYER_CONTEXT}."
        ),
        HumanMessage(content=context),
    ]

    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    response = llm.invoke(messages)
    response_content = {"title": title, "player_info": response.content}
    return parse_player_info(response_content["player_info"])


# Write player information to Firestore
def write_to_firestore(player_info: dict):
    doc_ref = db.collection("player_info").document(player_info["name"])
    doc = doc_ref.get()

    if doc.exists:
        new_info = player_info.get("info", [])
        if new_info:
            doc_ref.update({"info": firestore.ArrayUnion(new_info)})
    else:
        doc_ref.set(player_info)
