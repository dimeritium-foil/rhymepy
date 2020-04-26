# for fetching rhymes from an api (datamuse)

from os import popen
import requests
import json

# fetch rhymes from the datamuse api
def datamuse_rhymes(word, datamuse_option):

    url = "https://api.datamuse.com/words?"

    if datamuse_option == 0:
        datamuse_response = requests.get(url + "rel_rhy=" + word).json()
    elif datamuse_option == 1:
        datamuse_response = requests.get(url + "rel_nry=" + word).json()
    else:
        perfect_rhymes = requests.get(url + "rel_rhy=" + word).json()
        approximate_rhymes = requests.get(url + "rel_nry=" + word).json()

        datamuse_response = perfect_rhymes + approximate_rhymes

    rhymes_list = []

    for entry in datamuse_response:
        rhymes_list.append(entry["word"])

    return rhymes_list

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
