import dataclasses
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Union, Optional, Set

import tree_sitter

from buckwheat.subtokenizer import TokenParser
from buckwheat.type_specs import IDENTIFIER_TYPES

tokenizer = TokenParser()


class ProgrammingLanguages(Enum):
    CPP = "C++"
    TSX = "TSX"
    JS = "JavaScript"
    GO = "Go"
    JAVA = "Java"
    RUBY = "Ruby"
    TS = "TypeScript"
    PHP = "PHP"
    CSHARP = "C#"
    C = "C"
    SHELL = "Shell"
    RUST = "Rust"
    SCALA = "Scala"
    SWIFT = "Swift"
    KOTLIN = "Kotlin"
    HASKELL = "Haskell"
    PYTHON = "Python"


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
    language: ProgrammingLanguages


@dataclass
class Repository:
    """Repository with list of classified files"""
    path: str
    language_file_index: Dict[str, List[str]]


@dataclass
class EntityPosition:
    start_byte: int
    start_line: int
    start_column: int
    end_byte: int
    end_line: int
    end_column: int


@dataclass
class TreeSitterNode:
    node: Optional[tree_sitter.Node]
    children: List["TreeSitterNode"] = field(default_factory=list)


@dataclass
class HeadlessEntity:
    position: Optional[EntityPosition] = None
    object_type: Optional[str] = None
    node: Optional[tree_sitter.Node] = None

    @classmethod
    def construct_from_node(cls, node: tree_sitter.Node, with_position: bool = False, with_node: bool = False)\
            -> "HeadlessEntity":
        position = None

        if with_position:
            start_line, start_column = node.start_point
            end_line, end_column = node.end_point
            position = EntityPosition(node.start_byte, start_line, start_column, node.end_byte, end_line, end_column)

        tree_sitter_node = node if with_node else None
        return cls(position, node.type, tree_sitter_node)

    @property
    def node_id(self):
        assert self.node
        return f"{self.node.start_byte}:{self.node.end_byte}"

    def parent_of_type(self, types: Set[str]) -> Optional["HeadlessEntity"]:
        cursor: tree_sitter.TreeCursor = self.node.walk()
        has_next_parent = True

        while has_next_parent:
            has_next_parent = cursor.goto_parent()
            node: tree_sitter.Node = cursor.node

            if node.type in types:
                with_position = self.position is not None
                return self.construct_from_node(node, with_position=with_position, with_node=True)


@dataclass
class Entity(HeadlessEntity):
    # Maybe no inheritance ?
    body: str = ""

    @classmethod
    def construct_from_node_and_code(cls, node: tree_sitter.Node, code: str, with_position: bool = False,
                                     with_node: bool = False) -> "Entity":
        position = None

        if with_position:
            start_line, start_column = node.start_point
            end_line, end_column = node.end_point
            position = EntityPosition(node.start_byte, start_line, start_column, node.end_byte, end_line, end_column)

        tree_sitter_node = node if with_node else None

        return cls(
            body=code[node.start_byte:node.end_byte],
            position=position,
            object_type=node.type,
            node=tree_sitter_node
        )

    # TODO: Probably extract to functions/classes to make pipeline more extensible
    @property
    def vowpal_compact_format(self):
        assert self.is_identifier
        return self.body

    @property
    def vowpal_verbose_format(self):
        assert self.is_identifier
        if self.position is None:
            raise ValueError("Entities should be extracted with position to verbose vowpal format")
        return f"{self.body}:{self.position.start_byte},{self.position.start_line},{self.position.start_column}"

    @property
    def is_identifier(self):
        return self.object_type in IDENTIFIER_TYPES

    @property
    def subtokens(self) -> List["Entity"]:
        if self.is_identifier:
            return [
                Entity(body=body_token, position=self.position, object_type=self.object_type, node=self.node)
                for body_token in tokenizer.process_token(self.body)
            ]

        return [self]
