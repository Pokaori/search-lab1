from math import log

from terms_settings import TermsSettings, DocumentTerms
from collections import Counter
from structures import TermDocumentInfo


class DocumentController:
    def __init__(self):
        self.__settings = TermsSettings()
        self.__documents: dict[str, DocumentTerms] = {}

    def save_documents(self, documents: dict[str, Counter]):
        self.__documents = {filename: {key: TermDocumentInfo(document[key]) for key in document} for filename, document
                            in
                            documents.items()}
        index_terms = self.__settings.index_terms
        for key, value in index_terms.items():
            index_terms[key].doc_count = 0
            for document in self.__documents.values():
                if key in document:
                    value.doc_count += 1
        self.__settings.index_terms = index_terms
        self._calculate()
        self._save()

    def _calculate(self):
        for document in self.__documents:
            terms_count = {term: value.doc_count for term, value in self.__settings.index_terms.items() if
                           term in self.__documents[document]}
            max_n = max(terms_count.values())
            for term in self.__documents[document]:
                n = self.__settings.index_terms[term].doc_count
                self.__documents[document][term].idf = self._idf(n, max_n)
                max_count = max(
                    self.__documents[doc][term].count for doc in self.__documents if self.__documents[doc].get(term))
                self.__documents[document][term].tf = self._tf(self.__documents[document][term].count, max_count)
                self.__documents[document][term].tf_idf = self.__documents[document][term].tf * \
                                                          self.__documents[document][term].idf

    @staticmethod
    def _tf(count, max_count) -> float:
        return 0.5 + 0.5 * count / max_count

    @staticmethod
    def _idf(n, max_n) -> float:
        return log(max_n / (1 + n))

    def _save(self):
        self.__settings.documents_terms = self.__documents
