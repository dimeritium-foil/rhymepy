# for fetching rhymes from an api, and caching the response
# also provides a progress bar

from os import popen, listdir
from pathlib import Path
import requests
import json

# fetch rhymes from the datamuse api
def datamuse_rhymes(word, datamuse_option):

    url = "https://api.datamuse.com/words?"

    if datamuse_option == 0:
        
        cache = word_cache_exists(word, "datamuse", "rhy")

        if cache["state"]:
            datamuse_response = cache["response"]
        else:
            datamuse_response = requests.get(url + "rel_rhy=" + word).json()
            cache_word(word, datamuse_response, "datamuse", "rhy")

    elif datamuse_option == 1:

        cache = word_cache_exists(word, "datamuse", "nry")

        if cache["state"]:
            datamuse_response = cache["response"]
        else:
            datamuse_response = requests.get(url + "rel_nry=" + word).json()
            cache_word(word, datamuse_response, "datamuse", "nry")

    else:

        cache_rhy = word_cache_exists(word, "datamuse", "rhy")
        cache_nry = word_cache_exists(word, "datamuse", "nry")

        if cache_rhy["state"] and cache_nry["state"]:
            datamuse_response = cache_rhy["response"] + cache_nry["response"]

        elif cache_rhy["state"]:
            approximate_rhymes = requests.get(url + "rel_nry=" + word).json()
            datamuse_response = cache_rhy["response"] + approximate_rhymes

            cache_word(word, approximate_rhymes, "datamuse", "nry")

        elif cache_nry["state"]:
            perfect_rhymes = requests.get(url + "rel_rhy=" + word).json()
            datamuse_response = cache_nry["response"] + perfect_rhymes

            cache_word(word, perfect_rhymes, "datamuse", "rhy")
        
        else:
            perfect_rhymes = requests.get(url + "rel_rhy=" + word).json()
            approximate_rhymes = requests.get(url + "rel_nry=" + word).json()

            datamuse_response = perfect_rhymes + approximate_rhymes

            cache_word(word, perfect_rhymes, "datamuse", "rhy")
            cache_word(word, approximate_rhymes, "datamuse", "nry")

    rhymes_list = []

    for entry in datamuse_response:
        rhymes_list.append(entry["word"])

    return rhymes_list

def cache_word(word, api_response, api_name, extra_api_info):

    cache_dir = Path("~/.cache/rhymepy/" + api_name).expanduser()

    if not cache_dir.exists():
        cache_dir.mkdir(parents=True)

    if extra_api_info is None:
        extra_api_info = ""
    else:
        extra_api_info += "_"

    word_file = open(str(cache_dir) + "/" + extra_api_info + word + ".json", "w")
    word_file.write(json.dumps(api_response))
    word_file.close()

def word_cache_exists(word, api_name, extra_api_info):

    cache_dir = Path("~/.cache/rhymepy/" + api_name).expanduser()

    if not cache_dir.exists():
        cache_dir.mkdir(parents=True)

    if extra_api_info is None:
        extra_api_info = ""
    else:
        extra_api_info += "_"

    cached_words = [word.replace(".json", "") for word in listdir(cache_dir)]

    search_word = extra_api_info + word

    if search_word in cached_words:
        
        word_file = open(str(cache_dir) + "/" + extra_api_info + word + ".json", "r")
        response = word_file.read()
        word_file.close()

        return {"state": True, "response": json.loads(response)}
    else:
        return {"state": False}

def progress_bar(passed, total):
    
    progress_chars = "[#-]"

    message = "fetching rhymes..."
    message_counter = str(passed) + " / " + str(total)

    # subtracting 2 from the width to account for the end chars
    term_width = int( popen("tput cols", "r").read() ) - 2

    fill = int( (passed/total)*term_width )

    # so that it doesn't overwrite the terminal prompt the first time, and also hide the cursor
    if passed == 1:
        print("\n")
        print("\033[?25l", end='') # hide cursor

    # overwrite the previously written 2 lines
    print("\033[F" * 2 ,end='')

    # print the message
    print(message, end='')
    print(" " * (term_width+2 - len(message) - len(message_counter)), end='')
    print(message_counter)

    # print the progress bar
    print(progress_chars[0],                       end='')
    print(progress_chars[1] * fill,                end='')
    print(progress_chars[2] * (term_width - fill), end='')
    print(progress_chars[3])
