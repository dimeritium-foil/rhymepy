# for parsing the command-line arguments and the config file

from pathlib import Path
from shutil import copyfile
import configparser
import argparse

def parse_arguments():

    parser = argparse.ArgumentParser()

    parser.add_argument("file", help="path to a txt file", nargs="?")

    lines_group = parser.add_mutually_exclusive_group()

    lines_group.add_argument(
                            "-l", "--lines",
                            type=int,
                            metavar="N",
                            help="number of lines to match rhymes"
                            )
    lines_group.add_argument(
                            "-a", "--all-lines",
                            action="store_true",
                            help="match all lines"
                            )
    lines_group.add_argument(
                            "-s", "--stanzas",
                            action="store_true",
                            help="match each stanza"
                            )

    parser.add_argument(
                       "--clear-cache",
                       action="store_true",
                       help="clear the cache folder and exit"
                       )

    x_backend_group = parser.add_argument_group("backends")
    backend_group = x_backend_group.add_mutually_exclusive_group()

    backend_group.add_argument(
                              "-p", "--pronouncing",
                              action="store_true",
                              help="use pronouncing as the backend for fetching rhymes"
                              )
    backend_group.add_argument(
                              "-d", "--datamuse",
                              type=int,
                              choices=[0, 1, 2],
                              help="use datamuse as the backend for fetching rhymes.0: match perfect rhymes. 1: match approximate rhymes. 2: match both"
                              )

    parser._positionals.title = "required arguments"

    return parser.parse_args()

def parse_config():

    config_dir_path = Path("~/.config/rhymepy/").expanduser()
    config_file_path = Path("~/.config/rhymepy/rhymepy.ini").expanduser()

    if not config_file_path.exists():
        create_default_config(config_dir_path, config_file_path)

    config = configparser.ConfigParser()
    config.read(config_file_path)

    try:
        colors = [int(num) for num in config["defaults"]["colors"].split()]
    except ValueError:
        print("config file error: invalid value for colors.")
        exit()
    except KeyError:
        print("config file error: colors not defined")
        exit()

    try:
        match = config["defaults"]["match"]
    except:
        print("config file error: match not defined.")
        exit()

    if match not in ["lines", "stanzas", "all"]:
        print("config file error: invalid value for match.")
        exit()

    try:
        match_lines = int( config["defaults"]["lines"] )
    except ValueError:
        print("config file error: invalid value for lines.")
        exit()
    except KeyError:
        print("config file error: lines is not defined.")
    
    if match_lines <= 0:
        print("config file error: invalid value for lines.")
        exit()

    try:
        backend = config["defaults"]["backend"]
    except:
        print("config file error: backend not defined.")

    if backend not in ["pronouncing", "datamuse"]:
        print("config file error: invalid value for backend.")
        exit()

    try:
        datamuse_option = int( config["defaults"]["datamuse-option"] )
    except ValueError:
        print("config file error: invalid value for datamuse-option.")
        exit()
    except KeyError:
        print("config file error: datamuse-option not defined.")
        exit()

    if datamuse_option not in [0, 1, 2]:
        print("config file error: invalid value for datamuse-option.")
        exit()

    defaults = {
                "colors": colors,
                "match": match,
                "match_lines": match_lines,
                "backend": backend,
                "datamuse_option": datamuse_option
               }

    return defaults

def create_default_config(dir_path, file_path):

    default_config_path = str(Path(__file__).parent) + "/" + "default_rhymepy.ini"

    if not Path(dir_path).exists():
        Path(dir_path).mkdir(parents=True)

    if not Path(file_path).exists():
        copyfile(default_config_path, file_path)

    print("config file not found, coping default config to", file_path)
