from collections import deque
from dataclasses import dataclass
from typing import List, Iterable, Generator, Tuple, Set, Dict, Optional

import pygments
from pygments.lexers.haskell import HaskellLexer
from pygments.lexers.jvm import ScalaLexer, KotlinLexer
from pygments.lexers.objective import SwiftLexer
import tree_sitter

from buckwheat.parsing.utils import get_parser
from buckwheat.tokenizer import TreeSitterParser
from buckwheat.types import Entity, ProgrammingLanguages, LanguageClassifiedFile, TreeSitterNode


class BaseEntityExtractor:

    def parse_entities(self, code: str) -> List[Entity]:
        raise NotImplementedError


@dataclass
class TreeSitterExtractor(BaseEntityExtractor):
    language: ProgrammingLanguages
    types: Set[str]
    # TODO: Make this configurable
    verbose: bool = True
    traversable: bool = True

    def parse_entities(self, code: str) -> Generator[Entity, None, None]:
        parser = get_parser(TreeSitterParser.PARSERS[self.language.value])
        tree: tree_sitter.Tree = parser.parse(code.encode())
        cursor: tree_sitter.TreeCursor = tree.walk()

        has_next_node = True

        while has_next_node:
            node: tree_sitter.Node = cursor.node
            has_next_node = cursor.goto_first_child() or cursor.goto_parent() and cursor.goto_next_sibling()

            if node.type in self.types:
                yield Entity.construct_from_node_and_code(node, code, self.verbose, self.traversable)


# Pygments lexers corresponding to a given language.
_PYGMENTS_LEXERS = {
    "Scala": ScalaLexer(),
    "Swift": SwiftLexer(),
    "Kotlin": KotlinLexer(),
    "Haskell": HaskellLexer(),
}


# Pygments token types corresponding to identifiers in a given language.
_PYGMENTS_IDENTIFIERS = {
    "Scala": {pygments.token.Name, pygments.token.Keyword.Type},
    "Swift": {pygments.token.Name},
    "Kotlin": {pygments.token.Name},
    "Haskell": {pygments.token.Name, pygments.token.Keyword.Type},
}


@dataclass
class PygmentsExtractor(BaseEntityExtractor):
    language: ProgrammingLanguages

    def __post_init__(self):
        # TODO: Better naming
        self.types = _PYGMENTS_IDENTIFIERS[self.language.value]
        self.lexer = _PYGMENTS_LEXERS[self.language.value]

    def parse_entities(self, code: str) -> List[Entity]:
        for token_type, token in pygments.lex(code, self.lexer):
            if any(token_type in token_types for token_types in self.types):
                yield Entity(token, object_type=token_type)


def build_entities_extractor(extractors_spec: Dict[ProgrammingLanguages, BaseEntityExtractor]):
    def entity_extractor(file: LanguageClassifiedFile) -> List[Entity]:
        if file.language not in extractors_spec:
            return []
        extractor = extractors_spec[file.language]
        with open(file.path, "r", encoding="utf-8") as f:
            return list(extractor.parse_entities(f.read()))

    return entity_extractor


def subtokenize_identifiers(entity: Entity) -> List[Entity]:
    return entity.subtokens


def get_tree_sitter_spec(types_definition: Dict[str, Set[str]], parent_definition: Optional[Dict[str, Set[str]]]) \
        -> Dict[ProgrammingLanguages, TreeSitterExtractor]:
    languages = set(types_definition.keys()).intersection(set(parent_definition.keys()))

    return {
        ProgrammingLanguages(lang): TreeSitterExtractor(ProgrammingLanguages(lang), types_definition[lang])
        for lang in languages
    }


def get_pygments_extractor_spec(languages: List[str]) -> Dict[ProgrammingLanguages, PygmentsExtractor]:
    return {ProgrammingLanguages(lang): PygmentsExtractor(ProgrammingLanguages(lang)) for lang in languages}
