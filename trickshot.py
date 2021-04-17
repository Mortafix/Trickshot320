from json import load, loads
from os import path, walk
from re import match, sub
from time import sleep

from colorifix.colorifix import Color, paint
from halo import Halo
from requests import post
from youtube_dl import YoutubeDL

# --- PARAMS
CONFIG = load(open("config.json"))
SONGS_FOLDER = CONFIG.get("song-folder")
DOWNLOADED_SONG_FOLDER = CONFIG.get("downloaded-folder")
API_URL = CONFIG.get("api-url")
DOWLOAD_URL = CONFIG.get("download-url")
DEBUG = CONFIG.get("debug")
SPINNER = Halo()

# --- COLORS
colored = CONFIG.get("color")
colors = (
    {
        "blue": Color.BLUE,
        "red": Color.RED,
        "green": Color.GREEN,
        "magenta": Color.MAGENTA,
        "cyan": Color.CYAN,
        "yellow": Color.YELLOW,
        "white": Color.WHITE,
    }
    if colored
    else {}
)
base_color = Color.WHITE if colored else None
color_action = colors.get(CONFIG.get("colors").get("actions"), base_color)
color_search = colors.get(CONFIG.get("colors").get("title-searching"), base_color)
color_found = colors.get(CONFIG.get("colors").get("song-found"), base_color)


def encryptD(number):
    o = list("ABCDEFGHJKMNPQRSTUVWXYZabcdefghjkmnpqrstuvxyz123")
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
    PARAMS = {"q": query.strip(), "page": 0, "sort": 0}
    result = post(API_URL, data=PARAMS).text
    return loads(result[1:-2]).get("response")


def get_download_link_first_song(songs_list):
    if not songs_list:
        return None, None, None
    song = songs_list[1]
    url = f"{DOWLOAD_URL}{encryptD(song.get('owner_id'))}:{encryptD(song.get('id'))}"
    return song.get("title"), song.get("artist"), url


def download_audio(url, filename):
    with YoutubeDL(
        {
            "outtmpl": f"{filename}.mp3",
            "quiet": True,
            "no_warnings": True,
            "ignoreerrors": True,
            "nocheckcertificate": True,
        }
    ) as ydl:
        ydl.download([url])


def spinner(func, action, search, artist=None, title=None):
    func(
        paint(f"{action} ", color_action)
        + paint(search, color_search)
        + (
            " [" + paint(f"{artist} - {title}", color_found) + "]"
            if artist and title
            else ""
        )
    )


def main():
    if not path.exists(SONGS_FOLDER):
        print(paint(f"Folder '{SONGS_FOLDER}' doens't exists.", Color.RED))
        exit(-1)
    for file in filter(lambda x: not match(r"\.", x), list(walk(SONGS_FOLDER))[0][2]):
        query = path.splitext(file)[0].replace("_", " ")
        query = sub(r"\(.*\)", "", sub(r"\[.*\]", "", query))
        if not DEBUG:
            spinner(SPINNER.start, "Searching", query)
        try:
            for _ in range(10):
                song_list = get_songs_list(query)
                if song_list:
                    title, artist, url = get_download_link_first_song(song_list)
                    break
                url = None
                sleep(0.2)
            if url:
                if not DEBUG:
                    spinner(SPINNER.start, "Downloading", query, artist, title)
                download_audio(
                    url, path.join(SONGS_FOLDER, DOWNLOADED_SONG_FOLDER, query)
                )
                if not DEBUG:
                    spinner(SPINNER.succeed, "Downloaded", query, artist, title)
            elif not DEBUG:
                spinner(SPINNER.fail, "Not found", query)
        except Exception:
            if not DEBUG:
                spinner(SPINNER.fail, "Error", query)


if __name__ == "__main__":
    main()
