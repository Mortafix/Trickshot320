from json import loads
from os import path, walk
from re import sub
from time import sleep

from colorifix.colorifix import Color, paint
from halo import Halo
from requests import post
from youtube_dl import YoutubeDL

API_URL = "https://myfreemp3music.com/api/search.php"
SONGS_FOLDER = ""
DOWNLOADED_SONG_FOLDER = ""


def encryptD(number):
    o = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "J",
        "K",
        "M",
        "N",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
        "Z",
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "j",
        "k",
        "m",
        "n",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "x",
        "y",
        "z",
        "1",
        "2",
        "3",
    ]
    length = len(o)
    e = ""
    if number < 0:
        number *= -1
        e = "-"
    if number == 0:
        return o[0]
    while number > 0:
        e += o[number % length]
        number //= length
    return e


def get_songs_list(query):
    PARAMS = {"q": query.lower(), "page": 0, "sort": 0}
    result = post(API_URL, data=PARAMS).text
    return loads(result[1:-2])


def get_download_link_first_song(songs_list):
    response = songs_list.get("response")
    if not response:
        return None, None
    song = response[1]
    aid = song.get("id")
    oid = song.get("owner_id")
    url = f"https://speed.idmp3s.com/{encryptD(oid)}:{encryptD(aid)}"
    return song.get("title"), url


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
        query = sub(r"\(.*\)", "", sub(r"\[.*\]", "", query))
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
