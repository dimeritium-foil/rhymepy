#!/bin/env python3

# this was made during the infamous 2020 quarantine
# https://github.com/dimeritium-foil/rhymepy

from string import punctuation
from colored import bg, attr
import argparse
import requests
import json

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
    parse_args(parser)
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

    # apply the chosen backend and default to pronouncing if it exists
    if pronouncing_exists and args.pronouncing:
        backend = "pronouncing"
    elif args.datamuse is not None:
        backend = "datamuse"
        datamuse_option = args.datamuse
    elif pronouncing_exists:
        backend = "pronouncing"
    else:
        backend = "datamuse"

    generate_rhymes_struct(backend)

    match_rhyming_words(lines_to_match)

    # print the poem after colorizing the matches
    for line in poem:
        print(*line, sep=' ')

def parse_args(parser):

    parser.add_argument("file", help="a txt file")

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


# looks for a word in the rhymes_struct, and returns the key if it exists
def exists(word):

    for key in rhymes_struct:
        if word in rhymes_struct[key]:
            return {"state": True, "key": key}

    return {"state": False}

# generate a dictionary where each key is a list of words that rhyme in the whole poem
def generate_rhymes_struct(backend):

    count = 0
    for test_line in poem:
        for test_word in test_line:

            # check if the current line is empty
            if test_line == []:
                break

            test_word = test_word.strip(punctuation)
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

                    word = word.strip(punctuation)

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

# find rhyming words for each block of lines, and match them together via colorizing
def match_rhyming_words(lines):

    color_index = 0

    for i in range(0, len(poem), lines):

        lines_block = flatten(poem[i:i + lines])

        # strip all words' punctuation for proper matching
        for j in range(len(lines_block)):
            lines_block[j] = lines_block[j].strip(punctuation)

        for key in rhymes_struct:

            matching_words = list(set(lines_block).intersection(rhymes_struct[key])) 

            if matching_words != [] and len(matching_words) > 1:

                color_index += 1
                colorize_words(matching_words, i, i + lines, color_index)

# merges a list of lists into a single list
def flatten(lines):

    flat = []
    for i in lines:
        for j in i:
            flat.append(j)

    return flat

# color the matching words generated by match_rhyming_words with the same color
def colorize_words(matching_words_list, line_start, line_end, color_index):

    for i in range(line_start, line_end):
        try:
            for j in range(len(poem[i])):

                if poem[i][j].strip(punctuation) in matching_words_list:
                    poem[i][j] = bg(color_index) + poem[i][j] + attr(0)
        except:
            pass

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

main()
