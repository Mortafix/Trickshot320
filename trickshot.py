from json import loads
from os import path, walk
from time import sleep

from colorifix.colorifix import Color, paint
from halo import Halo
from requests import post
from youtube_dl import YoutubeDL

API_URL = "https://myfreemp3music.com/api/search.php"
SONGS_FOLDER = "/Users/Moris/Desktop/songs"
DOWNLOADED_SONG_FOLDER = "MyFreeMP3"


def get_songs_list(query):
    PARAMS = {"q": query.lower(), "page": 0, "sort": 0}
    result = post(API_URL, data=PARAMS).text
    return loads(result[1:-2])


def get_download_link_first_song(songs_list):
    response = songs_list.get("response")
    if not response:
        return None, None
    return response[1].get("title"), response[1].get("url")


def download_audio(url, filename):
    with YoutubeDL(
        {"outtmpl": f"{filename}.mp3", "quiet": True, "no_warnings": True}
    ) as ydl:
        ydl.download([url])


def main():
    SPINNER = Halo()
    # Folder scan
    _, _, files = list(walk(SONGS_FOLDER))[0]
    for file in files:
        query = path.splitext(file)[0].replace("_", " ")
        # MyFreeMP3
        SPINNER.start(paint("Searching ", Color.WHITE) + paint(query, Color.BLUE))
        for _ in range(5):
            song_list = get_songs_list(query)
            title, url = get_download_link_first_song(song_list)
            if url:
                break
            sleep(1)
        if url:
            SPINNER.start(paint("Downloading ", Color.WHITE) + paint(title, Color.BLUE))
            download_audio(url, path.join(SONGS_FOLDER, DOWNLOADED_SONG_FOLDER, query))
            SPINNER.succeed(
                paint("Downloaded ", Color.WHITE) + paint(title, Color.BLUE)
            )
        else:
            SPINNER.fail(paint("Error ", Color.WHITE) + paint(query, Color.BLUE))


if __name__ == "__main__":
    main()
