import re
from dataclasses import asdict, is_dataclass
from copy import deepcopy
import json
from typing import TypeAlias
from structures import TermDocumentInfo, TermIndexInfo

DocumentTerms: TypeAlias = dict[str, TermDocumentInfo]
IndexTerms: TypeAlias = dict[str: TermIndexInfo]


class DataclassJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)


class TermsSettings:
    def __init__(self, path: str = "settings_terms.json"):
        self.__path = path
        self.__index_key = "indexes"
        self.__term_key = "terms"
        with open(self.__path, "r") as f:
            settings = json.load(f)
        self.__index_terms: IndexTerms = {key: TermIndexInfo(**value) for key, value in
                                          settings.get(self.__index_key, {}).items()}
        self.__files_terms: dict[str, DocumentTerms] = {
            file: {term: TermDocumentInfo(**data) for term, data in value.items()}
            for file, value in settings.get(self.__term_key, {}).items()}

    @property
    def documents_terms(self) -> dict[str, DocumentTerms]:
        return deepcopy(self.__files_terms)

    @documents_terms.setter
    def documents_terms(self, value: DocumentTerms):
        self.__files_terms = value

        # self.__files_terms = {key: {re.findall(r'\w+', w)[0].lower(): {} for w in terms} for key, terms in value.items()}
        self.__settings_save()

    @property
    def index_terms(self) -> IndexTerms:
        return deepcopy(self.__index_terms)

    @index_terms.setter
    def index_terms(self, value: IndexTerms):
        self.__index_terms = value
        # self.__index_terms = [re.findall(r'\w+', w)[0].lower() for w in value]
        self.__settings_save()

    def __settings_save(self):
        with open(self.__path, "r") as f:
            settings = json.load(f)
        settings[self.__term_key] = self.__files_terms
        settings[self.__index_key] = self.__index_terms
        with open(self.__path, "w") as f:
            json.dump(settings, f, indent=4, cls=DataclassJSONEncoder)
