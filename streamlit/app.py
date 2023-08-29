import os

from dotenv import find_dotenv, load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
from googleapiclient.discovery import build

import streamlit as st

# find .env automagically by walking up directories until it's found
dotenv_path = find_dotenv()

# load up the entries as environment variables
load_dotenv(dotenv_path)

DEVELOPER_KEY = os.environ.get("YOUTUBE_DEVELOPER_KEY")
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
ELASTIC_PASSWORD = os.environ.get("ELASTIC_USER_PASSWORD")


def youtube_search(q, max_results):
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

    # Call the search.list method to retrieve results matching the specified query term.
    search_response = (
        youtube.search()
        .list(
            q=q,
            part="id,snippet",
            maxResults=max_results,
        )
        .execute()
    )

    video_details = []

    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            video_details.append(
                {
                    "title": search_result["snippet"]["title"],
                    "video": search_result["id"]["videoId"],
                    "description": search_result["snippet"]["description"],
                }
            )
    return video_details


def search_result(i: int, url: str, title: str, headline: str, **kwargs) -> str:
    """HTML scripts to display search results."""
    return f"""
        <div style="font-size:120%;">
            {i + 1}.
            <a href="{url}">
                {title}
            </a>
        </div>
        <div style="font-size:95%;">
         <div style="color:grey;font-size:95%;">
                {url[:90] + '...' if len(url) > 100 else url}
            </div>
            <div style="float:left;font-style:italic;">
                {headline} ·&nbsp;
            </div>
        </div>
    """


def main():
    st.title("Search a Udemy course")
    search = st.text_input("Enter search words:")

    INDEX = "udemy_data"
    es = Elasticsearch(
        hosts="http://elasticsearch:9200",
        # ca_certs="/streamlit/http_ca.crt",
        # http_auth=("elastic", ELASTIC_PASSWORD),
        # use_ssl=True,
        # verify_certs=False
    )

    print(es.indices.get("*"))

    if search:
        s = Search(using=es, index=INDEX).query("match", title=search)
        response = s.execute()

        # search results
        for index, hit in enumerate(response):
            videos_list = youtube_search(q=hit.headline, max_results=5)

            st.header("Udemy Course")
            st.write(
                search_result(
                    i=index,
                    url=f"https://www.udemy.com{hit.url}",
                    title=hit.title,
                    headline=hit.headline,
                ),
                unsafe_allow_html=True,
            )
            st.subheader("Related YouTube videos")
            for i, video in enumerate(videos_list):
                st.write(
                    search_result(
                        i=i,
                        url=f"https://www.youtube.com/{video['video']}",
                        title=video["title"],
                        headline=video["description"],
                    ),
                    unsafe_allow_html=True,
                )


if __name__ == "__main__":
    main()
