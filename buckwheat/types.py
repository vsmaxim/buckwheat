import dataclasses
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Union

import tree_sitter


class ObjectTypes(Enum):
    CLASS = "class"
    FUNCTION = "function"


class IdentifiersTypes(Enum):
    """
    string = identifier itself
    verbose = IdentifierData class
    """
    STRING = "string"
    VERBOSE = "verbose"


# TODO: consider the differences between str and byte from the standpoint of coordinates
@dataclasses.dataclass
class IdentifierData:
    """
    Data class to store individual identifiers and their positional coordinates.
    """
    identifier: str
    start_byte: int
    start_line: int
    start_column: int

    def __str__(self):
        return self.identifier


@dataclasses.dataclass
class ObjectData:
    """
    Data class to store objects (classes and functions) and their parameters: positional
    coordinates, language and identifiers.
    """
    object_type: ObjectTypes
    identifiers: List[IdentifierData]
    content: str
    lang: str
    start_byte: int
    start_line: int
    start_column: int
    end_byte: int
    end_line: int
    end_column: int


@dataclasses.dataclass
class FileData:
    """
    Dataclass to store files and their content.
    """
    path: str
    lang: str
    objects: List[ObjectData]
    identifiers: Union[List[IdentifierData], List[str]]
    identifiers_type: IdentifiersTypes  # VERBOSE for IdentifierData, STRING for str.


@dataclass
class LanguageClassifiedFile:
    """File with classified language"""
    path: str
    language: str


@dataclass
class ASTParsedFile(LanguageClassifiedFile):
    """Parsed code file with code and parsed nodes list"""
    code: bytes
    # TODO: May be iterable but think how to avoid recomputation of nodes
    nodes: List[tree_sitter.Node]

    @property
    def is_empty(self) -> bool:
        return not len(self.code)


@dataclass
class ASTNode:
    """Single node from file"""
    node: tree_sitter.Node
    file: ASTParsedFile


@dataclass
class IdentifiersParsedNode:
    """Parsed node from file with list of identifiers"""
    file: str
    identifiers: List[IdentifierData]


@dataclass
class ObjectsParsedNode:
    """Parsed node from file with list of objects"""
    file: str
    language: str
    objects: List[ObjectData]


@dataclass
class Repository:
    """Repository with list of classified files"""
    path: str
    language_file_index: Dict[str, List[str]]

