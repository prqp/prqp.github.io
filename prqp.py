"""
PRQP ml to html

by ξ
"""

import os
import re
from enum import Enum
from itertools import groupby
from pprint import pprint as pp
from datetime import datetime
import json

# .. CONFIG ..
PAGES_DIR = "pages"
PAGES_EXT = ".prqp"
BUILD_DIR = "build"
BUILD_EXT = "html"
# ..        ..

# .. LANGUAGE ..
TRANSPILE_COMMENTS = True
class Tokens(Enum):
    DATA = r'\.(.[^ ]*) (.*)'  # $1: data,   $2: value
    HEADER = r'=(\d*) (.*)'    # $1: level,  $2: header
    LINK = r'\[(.+)\]\((.*)\)' # $1: text,   $2: url
    IMAGE = r'{(.+)}'          # $1: path
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

    addPar(par)
    return grouped


def tokenize(pages):
    return {
        page: groupPar([
            matchLine(line) for line in content
        ]) for page, content in pages.items()
    }


def transpileToken(token, data):
    if token == Tokens.HEADER:
        level = data[0] if data[0] else '1'
        return f'<h{level}>{data[1]}</h{level}>'
    elif token == Tokens.TEXT:
        return f'<p>{"<br>".join(data)}</p>'
    elif token == Tokens.COMMENT and TRANSPILE_COMMENTS:
        return f'<!-- {data[0]} -->'
    elif token == Tokens.IMAGE:
        return f'<img src="/imgs/{data[0]}" alt="{data[0]}" />'
    elif token == Tokens.LINK:
        return f'<a href={data[1]}>{data[0]}</a>'


def transpile(tokens):
    return filter(
        lambda t: t is not None,
        [transpileToken(token, data) for token, data in tokens]
    )


def out_fname(path):
    fname = path.split('/')[-1].split('.')[0]
    return f'{BUILD_DIR}/{fname}.{BUILD_EXT}'


def build_menu(tokens):
    menu = []
    for page, ctx in tokens.items():
        entries = {}
        for token in ctx:
            if token[0] == Tokens.DATA:
                entries[token[1][0]] = token[1][1]
        entries['url'] = out_fname(page)
        menu.append(entries)
    return sorted(menu, key=lambda e: datetime.strptime(e['date'], '%d/%m/%y'))


if __name__ == "__main__":
    pages = get_pages()
    tokenized = tokenize(pages)
    
    for path, tokens in tokenized.items():
        html = transpile(tokens)
        with open(out_fname(path), 'w') as out:
          out.write('\n'.join(html))

    menu = build_menu(tokenized)
    with open(f'{BUILD_DIR}/pages.json', 'w') as out:
        out.write(json.dumps({ 'pages': menu }))