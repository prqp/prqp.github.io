"""
PRQP ml to html

by ξ
"""

"""
LANG EXAMPLE:

.data value
= header
paragraph
# comment
"""

"""
TODO
- parse .data (title, date, author, etc...)
- in-text markup
    - bold
    - italic
    - imgs
- build html pages from template
"""

import os
import re
from enum import Enum
from itertools import groupby
from pprint import pprint as pp

# .. CONFIG ..
PAGES_DIR = "pages"
PAGES_EXT = ".prqp"
# ..        ..

# .. LANGUAGE ..
TRANSPILE_COMMENTS = True
class Tokens(Enum):
    DATA = r'\.(.[^ ]*) (.*)'  # $1: data,   $2: value
    HEADER = r'= (.*)'         # $1: header
    COMMENT = r'# (.*)'        # $1: comment
    TEXT = r'(.*)'             # $1: content
# ..          ..


def get_page_content(path):
    with open(path) as page:
        return [l.strip() for l in page.readlines()]


def get_pages():
    return {
        page: get_page_content(page) for page in [
            os.path.join(PAGES_DIR, page) for page in os.listdir(PAGES_DIR)
            if os.path.splitext(page)[1] == PAGES_EXT
        ] if os.path.isfile(page)
    }


def matchLine(line):
    for token in Tokens:
        match = re.search(token.value, line)
        if (match):
            return (token, match.groups())
    return None


def groupPar(tokens):
    grouped = []
    par = []

    def addPar(par):
        if len(par) > 0:
            grouped.append((Tokens.TEXT, tuple(par)))
            return []
        return par

    for token, match in tokens:
        if token == Tokens.TEXT:
            par = addPar(par) if match[0] == '' else par + list(match)
        else:
            par = addPar(par)
            grouped.append((token, match))

    return grouped


def tokenize(pages):
    return {
        page: groupPar([
            matchLine(line) for line in content
        ]) for page, content in pages.items()
    }


def transpileToken(token, data):
    if token == Tokens.HEADER:
        return f'<h1>{data[0]}</h1>'
    elif token == Tokens.TEXT:
        return f'<p>{" ".join(data)}</p>'
    elif token == Tokens.COMMENT and TRANSPILE_COMMENTS:
        return f'<!-- {data[0]} -->'


def transpile(tokens):
    return filter(
        lambda t: t is not None,
        [transpileToken(token, data) for token, data in tokens]
    )


if __name__ == "__main__":
    pages = get_pages()
    tokenized = tokenize(pages)

    for path, tokens in tokenized.items():
        html = transpile(tokens)
        fname = path.split('/')[-1].split('.')[1]
        
        with open(f'build/{fname}.html', 'w') as out:
          out.write('\n'.join(html))
