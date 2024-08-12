#!/usr/bin/env python

import json
import os
import pickle

from helpers import parse_feed, parse_news_urls
from langchain import hub
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from fantasy_ai.news_service.player_context import player_context as PLAYER_CONTEXT

# os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY


def get_json_contents(folder: str):
    for file_name in os.listdir(folder):
        if file_name.endswith(".json"):
            with open(f"{folder}/{file_name}", "r") as f:
                data = json.load(f)
                yield (data["title"], data["contents"])


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

    file_path = "news_service/output/player_info.json"

    response_content = {"title": title, "player_info": response.content}

    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, "r") as file:
            data = json.load(file)
            data.append(response_content)
    else:
        data = [response_content]

    with open(file_path, "w") as file:
        json.dump(data, file)


def parse_player_info(data):
    results = []

    # Iterate through each article
    for article in data:
        title = article["title"]
        player_infos = article["player_info"].split(
            "\n\n"
        )  # Split into sections for each player

        # Iterate through each player section
        for player_info in player_infos:
            lines = player_info.split("\n")
            player_header = lines[0]

            # Extract player name, team, and position
            header_parts = player_header.split()
            if len(header_parts) < 3:
                continue  # Skip if the header is not complete
            player_name = " ".join(header_parts[1:-2]).strip()
            team_position = header_parts[-2:]
            team = team_position[0]
            position = team_position[1].replace(":", "")
            print(player_name, team, position)

            # Extract the list of infos
            info_list = lines[1:]  # Everything after the first line is info

            # Store the extracted information in a structured way
            player_dict = {
                "name": player_name,
                "team": team,
                "position": position,
                "info": info_list,
            }
            results.append(player_dict)

    return results


def save_vectorstore(vectorstore, filename):
    with open(filename, "wb") as f:
        pickle.dump(vectorstore, f)


def load_vectorstore(filename):
    with open(filename, "rb") as f:
        return pickle.load(f)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def create_vectorstore(player_info):
    vectorstore = {}
    docs = []
    for player in player_info:
        name = player["name"]
        team = player["team"]
        position = player["position"]
        info = player["info"]

        docs.append(
            Document(
                page_content=f"{name} {team} {position} {' '.join(info)}",
                metadata={"name": name},
            )
        )

    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=OpenAIEmbeddings(),
        collection_name="player_info",
        persist_directory="news_service/output",
    )

    vectorstore._persist_directory

    retriever = vectorstore.as_retriever()
    prompt = hub.pull("rlm/rag-prompt")
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    print(
        rag_chain.invoke(
            "Team A is considering trading for George Pickens from Team B. Write a funny paragraph summarizing the trade. Act as if you are a comedy writer for a sports website. Use some specifics from the context to make the paragraph more insightful."
        )
    )


if __name__ == "__main__":
    url = (
        "https://www.google.com/alerts/feeds/03680390526070901075/10636107894987274492"
    )
    # urls = parse_feed(url)
    # parse_news_urls(urls, "news_service/articles")
    # for title, contents in get_json_contents("news_service/articles"):
    #     extract_player_info(title, contents)

    # with open("news_service/output/player_info.json", "r") as file:
    #     data = json.load(file)

    # player_info = parse_player_info(data)
    # print(player_info)
    # with open("news_service/output/player_info_parsed.json", "w") as file:
    #     json.dump(player_info, file)

    with open("news_service/output/player_info_parsed.json", "r") as file:
        player_info = json.load(file)

    create_vectorstore(player_info)
