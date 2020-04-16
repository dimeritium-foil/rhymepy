#!/bin/env python3

# this was made during the infamous 2020 quarantine
# https://github.com/dimeritium-foil/rhymepy

from string import punctuation
from colored import bg, attr
from os import popen
import argparse
import requests
import json
import time
import atexit

# import the pronouncing library if it exists
try:
    from pronouncing import rhymes
    pronouncing_exists = True
except:
    pronouncing_exists = False

rhymes_struct = {}

def main():

    # parse command line arguments
    parser = argparse.ArgumentParser()
    parse_arguments(parser)
    args = parser.parse_args()

    # read the input file
    file = open(args.file, "r")
    input_file = file.read().splitlines()
    file.close()

    # generate a list of lines, where each line is a list of words, from the input file
    global poem
    poem = [word.split() for word in input_file]

    if args.all_lines:
        lines_to_match = len(poem)
    else:
        lines_to_match = args.lines

    # default value for datamuse rhyme matching. global so that it can be seen by the datamuse function
    global datamuse_option
    datamuse_option = 0

    backend = choose_backend(args)
    generate_rhymes_struct(backend)

    match_rhyming_words(lines_to_match)

    # print the final result
    term_width = int( popen("tput cols", "r").read() )
    print("")
    for i in range(len(poem)):

        # using input_file for the spaces count bec the color codes interfere
        spaces = (term_width - len(input_file[i])) // 2
        print(" " * spaces, end='')

        print(' '.join(poem[i]))

def parse_arguments(parser):

    parser.add_argument("file", help="path to a txt file")

    lines_group = parser.add_mutually_exclusive_group()
    lines_group.add_argument("-l", "--lines", type=int, default=2, 
                            help="number of lines to match rhymes (default: 2)", metavar="N")
    lines_group.add_argument("-a", "--all-lines", action="store_true", help="match all lines")

    x_backend_group = parser.add_argument_group("backends")
    backend_group = x_backend_group.add_mutually_exclusive_group()
    backend_group.add_argument("-p", "--pronouncing", action="store_true",
                       help="use pronouncing as the backend for fetching rhymes")

    backend_group.add_argument("-d", "--datamuse", type=int, choices=[0, 1, 2],
                        help="""use datamuse as the backend for fetching rhymes.
                             0: match perfect rhymes. 1: match approximate rhymes. 2: match both"""
                        )

    parser._positionals.title = "required arguments"

def choose_backend(args):

    # apply the chosen backend and default to pronouncing if it exists
    if pronouncing_exists and args.pronouncing:
        return "pronouncing"
    elif not pronouncing_exists and args.pronouncing:
        print("error: pronouncing isn't installed, you can install it by running 'pip install pronouncing'")
        exit()
    elif args.datamuse is not None:
        return "datamuse"
        datamuse_option = args.datamuse
    elif pronouncing_exists:
        return "pronouncing"
    else:
        return "datamuse"

# looks for a word in the rhymes_struct, and returns the key if it exists
def exists(word):

    for key in rhymes_struct:
        if word in rhymes_struct[key]:
            return {"state": True, "key": key}

    return {"state": False}


# generate a dictionary where each key is a list of words that rhyme in the whole poem
def generate_rhymes_struct(backend):

    # for the progress_bar if datamuse is chosen
    if backend == "datamuse":
        loading = 0
        words_sum = sum(len(line) for line in poem)
        start_time = time.time()

    count = 0
    for test_line in poem:
        for test_word in test_line:

            if backend == "datamuse":
                loading += 1
                progress_bar(loading, words_sum)

            # check if the current line is empty
            if test_line == []:
                break

            test_word = test_word.strip(punctuation).lower()
            first_test_word_existence = exists(test_word)

            # avoid fetching the rhyming words again if the word was already tested
            if first_test_word_existence["state"]:
                continue
            else:
                if backend == "datamuse":
                    rhyming_words = datamuse_rhymes(test_word)

                elif backend == "pronouncing":
                    rhyming_words = rhymes(test_word)
                else:
                    exit()

            for line in poem:
                for word in line:

                    word = word.strip(punctuation).lower()

                    if word in rhyming_words:

                        test_word_existence = exists(test_word)
                        word_existence = exists(word)
                        
                        # if both are already matched skip to the next word
                        if test_word_existence["state"] and word_existence["state"]:
                            continue

                        # if one of them exists add the other to the same list
                        elif test_word_existence["state"]:
                            rhymes_struct[test_word_existence["key"]].append(word)
                        elif word_existence["state"]:
                            rhymes_struct[word_existence["key"]].append(test_word)

                        # if it's a new match, add a new entry and add both words to it
                        else:
                            count += 1
                            rhymes_struct[count] = []
                            rhymes_struct[count].append(test_word)
                            rhymes_struct[count].append(word)


    if backend == "datamuse":
        elapsed_time = time.strftime("%Mm %Ss", time.gmtime(time.time() - start_time))
        print("elapsed time:", elapsed_time)

# find rhyming words for each block of lines, and match them together via colorizing
def match_rhyming_words(lines):

    color_index = 0
    count = 0
    lines_block = []

    for i in range(len(poem)):

        if poem[i] != []:
            lines_block += poem[i]
            count += 1
        else:
            continue

        if count == lines or i == len(poem) - 1:

            # strip all words' punctuation for proper matching
            for j in range(len(lines_block)):
                lines_block[j] = lines_block[j].strip(punctuation).lower()

            for key in rhymes_struct:

                matching_words = list(set(lines_block).intersection(rhymes_struct[key])) 

                if matching_words != [] and len(matching_words) > 1:

                    color_index += 1
                    colorize_words(matching_words, i - lines, i + 1, color_index)

            count = 0
            lines_block = []

# color the matching words generated by match_rhyming_words with the same color
def colorize_words(matching_words_list, line_start, line_end, color_index):

    for i in range(line_start, line_end):
        for j in range(len(poem[i])):

            if poem[i][j].strip(punctuation).lower() in matching_words_list:
                poem[i][j] = bg(colorize_index(color_index)) + poem[i][j] + attr(0)

# return color number from the color palette, with cycling
def colorize_index(index):

    colors = [1, 2, 3, 4, 237, 5, 6, 17, 22, 49, 54, 87, 52, 131, 213, 242, 208, 200, 20, 94]

    while index >= len(colors):
        index -= len(colors)

    return colors[index]

# fetch rhymes from the datamuse api
def datamuse_rhymes(word):

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
    print("\033[F \033[F", end='')

    # print the message
    print(message, end='')
    print(" " * (term_width - len(message) - len(message_counter)), end='')
    print(message_counter)

    # print the progress bar
    print(progress_chars[0],                       end='')
    print(progress_chars[1] * fill,                end='')
    print(progress_chars[2] * (term_width - fill), end='')
    print(progress_chars[3])

# show cursor again on exit in case it was hidden by the progress bar
def show_cursor():
    print("\033[?25h")
atexit.register(show_cursor)

main()
