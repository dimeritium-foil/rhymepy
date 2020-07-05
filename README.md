# rhymepy
A simple CLI program that highlights rhymes in a given text, using either the Datamuse API or the pronouncing module.

## Usage
```
usage: rhymepy [-h] [-l N | -a] [-p | -d {0,1,2}] file

required arguments:
  file                  a txt file

optional arguments:
  -h, --help            show this help message and exit
  -l N, --lines N       number of lines to match rhymes (default: 2)
  -a, --all-lines       match all lines
  -s, --stanzas         match each stanza  

backends:
  -p, --pronouncing     use pronouncing as the backend for fetching rhymes
  -d {0,1,2}, --datamuse {0,1,2}
                        use datamuse as the backend for fetching rhymes. 0: match perfect rhymes. 1: match approximate rhymes. 2: match both
```

## Example
<p align="center">
  <img src=https://raw.githubusercontent.com/dimeritium-foil/rhymepy/master/example.png />
</p>

Poem by [voodooattack](https://github.com/voodooattack).

## Installation
**Using pip**
```
$ pip install rhymepy
```

**Cloning the repository**
```
$ git clone https://github.com/dimeritium-foil/rhymepy
$ cd rhymepy
$ python setup.py install
```

## Dependencies
* [requests](https://pypi.org/project/requests/)
* [pronouncing](https://pypi.org/project/pronouncing/) (optional)
* [colored](https://pypi.org/project/colored/)
