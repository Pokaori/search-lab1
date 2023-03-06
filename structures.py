from dataclasses import dataclass, field


@dataclass
class ParsedQuery:
    words: list[str] = field(default_factory=list)
    signs: list[str] = field(default_factory=list)


@dataclass
class TermDocumentInfo:
    count: int
    tf: float = 0
    idf: float = 0
    tf_idf: float = 0


@dataclass
class TermIndexInfo:
    doc_count: int = 0
