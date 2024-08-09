#!/usr/bin/env python

from helpers import extract_player_info, parse_feed, parse_news_urls, write_to_firestore


def main():
    url = (
        "https://www.google.com/alerts/feeds/03680390526070901075/10636107894987274492"
    )
    urls = parse_feed(url)
    # iterate over the contents of the news articles
    for content in parse_news_urls(urls):
        # use llm to extract player information
        player_info = extract_player_info(content["title"], content["contents"])
        print(player_info)
        # write the player information to Firestore
        write_to_firestore(player_info)


if __name__ == "__main__":
    main()
