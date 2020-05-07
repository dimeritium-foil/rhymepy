# this was made during the infamous 2020 quarantine
# https://github.com/dimeritium-foil/rhymepy

from string import punctuation
from colored import bg, attr
from os import popen, getenv
from shutil import rmtree
import time
import atexit

# import the pronouncing library if it exists
try:
    from pronouncing import rhymes
    pronouncing_exists = True
except:
    pronouncing_exists = False

from .parse import parse_config, parse_arguments
from .apis import datamuse_rhymes, progress_bar

rhymes_struct = {}
defaults = {}

def main():

    # parse the config file first to set the defaults
    global defaults
    defaults = parse_config()

    # parse command line arguments
    args = parse_arguments()

    if args.clear_cache:
        rmtree(getenv("HOME") + "/.cache/rhymepy", ignore_errors=True)
        print("clearing cache")
        exit()

    # read the input file
    try:
        file = open(args.file, "r")
    except TypeError:
        print("error: no file specified")
        exit()
    except FileNotFoundError:
        print("error: file not found")
        exit()

    input_file = file.read().splitlines()
    file.close()

    # generate a list of lines, where each line is a list of words, from the input file
    global poem
    poem = [line.split() for line in input_file]

    backend = choose_backend(args)
    generate_rhymes_struct(backend)
    match_rhyming_words(args)

    print_result(input_file)

# takes the input file as an arg for the comparison
def print_result(input_file):

    # print the final result
    term_width = int( popen("tput cols", "r").read() )
    print("")
    for i in range(len(poem)):

        # using input_file for the spaces count bec the color codes interfere
        spaces = (term_width - len(input_file[i])) // 2
        print(" " * spaces, end='')

        print(' '.join(poem[i]))

def choose_backend(args):

    # so that it can be seen by the datamuse_rhymes function
    global datamuse_option

    # if no arguments specified, fallback to the defaults
    if args.pronouncing is False and args.datamuse is None:

        if defaults["backend"] == "pronouncing":
            if pronouncing_exists:
                return "pronouncing"
            else:
                print("error: pronouncing isn't installed, you can install it by running 'pip install pronouncing'")
                exit()
        else:
            datamuse_option = defaults["datamuse_option"]
            return "datamuse"

    if args.pronouncing:
        if pronouncing_exists:
            return "pronouncing"
        else:
            print("error: pronouncing isn't installed, you can install it by running 'pip install pronouncing'")
            exit()
    else:
        datamuse_option = args.datamuse
        return "datamuse"

# generate a dictionary where each key is a list of words that rhyme in the whole poem
def generate_rhymes_struct(backend):

    # looks for a word in the rhymes_struct, and returns the key if it exists
    def exists(word):

        for key in rhymes_struct:
            if word in rhymes_struct[key]:
                return {"state": True, "key": key}

        return {"state": False}

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
                    rhyming_words = datamuse_rhymes(test_word, datamuse_option)

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

def match_rhyming_words(args):

    # if no arguments specified, fallback to the defaults
    if args.all_lines is False and args.stanzas is False and args.lines is None:

        if defaults["match"] == "all":
            match_lines(len(poem))
        elif defaults["match"]  == "stanzas":
            match_stanzas()
        elif defaults["match"]  == "lines":
            match_lines(defaults["match_lines"])
        return

    if args.all_lines:
        match_lines(len(poem))
    elif args.stanzas:
        match_stanzas()
    elif args.lines <= 0:
        print("error: invalid number of lines")
        exit()
    else:
        match_lines(args.lines)

# find rhyming words for each block of lines, and match them together via colorizing
def match_lines(lines):

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

def match_stanzas():

    color_index = 0
    count = 0
    lines_block = []

    # add an empty line to the end of the poem to match the last stanza
    poem.append([])

    for i in range(len(poem)):

        if poem[i] != []:
            lines_block += poem[i]
            count += 1
        else:

            # strip all words' punctuation for proper matching
            for j in range(len(lines_block)):
                lines_block[j] = lines_block[j].strip(punctuation).lower()

            for key in rhymes_struct:

                matching_words = list(set(lines_block).intersection(rhymes_struct[key])) 

                if matching_words != [] and len(matching_words) > 1:

                    color_index += 1
                    colorize_words(matching_words, i - count, i + 1, color_index)

            count = 0
            lines_block = []

    # remove the added empty line
    del poem[len(poem) - 1]

# color the matching words generated by the matching function with the same color
def colorize_words(matching_words_list, line_start, line_end, color_index):

    for i in range(line_start, line_end):
        for j in range(len(poem[i])):

            if poem[i][j].strip(punctuation).lower() in matching_words_list:
                poem[i][j] = bg(colorize_index(color_index)) + poem[i][j] + attr(0)

# return color number from the color palette, with cycling
def colorize_index(index):

    colors = defaults["colors"]

    while index >= len(colors):
        index -= len(colors)

    return colors[index]

# show cursor again on exit in case it was hidden by the progress bar
def show_cursor():
    print("\033[?25h", end='')
atexit.register(show_cursor)

if __name__ == "__main__":
    main()
