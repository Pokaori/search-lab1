import re
from math import sqrt
from os import listdir
from os.path import isfile, join
from pathlib import Path
import json
import typer
from typing import List
from collections import Counter
from structures import ParsedQuery, TermIndexInfo
from terms_settings import TermsSettings
from document_controller import DocumentController

terms_storage = TermsSettings()
app = typer.Typer()

EDGE_VALUE = 0.05


def parse_boolean(query: str) -> ParsedQuery:
    start_i = 0
    signs_choice = {'|', '&'}
    pq = ParsedQuery()
    for i, let in enumerate(query):
        if let in signs_choice:
            if i - start_i == 0:
                print('Empty word, ignore sign')
                start_i = i + 1
                continue
            if word := re.findall(r'\w+', query[start_i:i]):
                pq.words.append(word[0].lower())
                pq.signs.append(let)
            else:
                print("Incorrect word, ignore next sign")
            start_i = i + 1
    if word := re.findall(r'\w+', query[start_i:len(query)]):
        pq.words.append(word[0].lower())
    else:
        print("Incorrect word, ignore next sign")
        pq.signs.pop()
    return pq


@app.command()
def index_terms(path: Path = typer.Option(
    ...,
    exists=True,
    file_okay=True,
    readable=True,
)):
    with open(path, 'r') as f:
        res = json.load(f)
    indexes = res['terms']
    try:
        terms_storage.index_terms = {index: TermIndexInfo() for index in indexes}
        terms_storage.documents_terms = {}
    except IndexError:
        print('Incorrect file structure. Should be dictionary with key "terms" and with list with non-containing words')
        raise typer.Abort()


@app.command()
def dir_documents(path: Path = typer.Option(
    ...,
    exists=True,
    dir_okay=True,
)):
    if not terms_storage.index_terms:
        print("No index terms. Please set index terms first!")
        raise typer.Abort()
    files = (join(path, f) for f in listdir(path) if isfile(join(path, f)))
    documents = {}
    for file in files:
        with open(file, 'r') as f:
            text = f.read()
        words = re.findall(r'\w+', text)
        words = Counter((w.lower() for w in words if w.lower() in terms_storage.index_terms))
        if words:
            documents[str(file)] = words
    DocumentController().save_documents(documents)


@app.command()
def find_boolean(query: str = typer.Option(...)):
    if not terms_storage.index_terms:
        print("No documents. Please set documents first!")
        raise typer.Abort()
    parse_query = parse_boolean(query)
    documents = {}
    for i, sign in enumerate(parse_query.signs):
        if not i:
            documents = {key for key, terms in terms_storage.documents_terms.items() if parse_query.words[i] in terms}
        word_set = {key for key, terms in terms_storage.documents_terms.items() if parse_query.words[i + 1] in terms}
        if sign == "|":
            documents |= word_set
        elif sign == "&":
            documents &= word_set


@app.command()
def find_vector(words: List[str] = typer.Argument(...)):
    files: {str, float} = {}
    for document, doc_terms in terms_storage.documents_terms.items():
        unique_words = set(doc_terms) & set(words)
        a = sum(doc_terms[w].tf_idf for w in unique_words)
        b = sqrt(sum(doc_terms[w].tf_idf ** 2 for w in doc_terms))*sqrt(len(words))
        if (similarity := a / b) > EDGE_VALUE:
            files[document] = similarity
    print(files)


# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    app()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
