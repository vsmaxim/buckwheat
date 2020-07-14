from typing import List, Set, Callable

from buckwheat.parsing.utils import get_parser
from buckwheat.tokenizer import subtokenize_identifier, TreeSitterParser
from buckwheat.types import ASTParsedFile, ASTNode, IdentifiersParsedNode, ObjectsParsedNode, LanguageClassifiedFile, \
    ObjectTypes
from buckwheat.utils import read_file

IdentifiersExtractor = Callable[[ASTNode], IdentifiersParsedNode]
ObjectsExtractor = Callable[[ASTNode], ObjectsParsedNode]


def build_nodes_extractor(types: Set[str]) -> Callable[[LanguageClassifiedFile], ASTParsedFile]:
    """
    Build nodes extractor for given set of types to extract.

    :param types: set of types to extract
    :return: nodes extractor function
    """

    def tokenize_files(file: LanguageClassifiedFile) -> ASTParsedFile:
        """
        Tokenize file and return parsed representation containing all parsed nodes from file

        :param file: file instance with classified language
        :return: parsed file with list of nodes
        """
        try:
            code = bytes(read_file(file.path), "utf-8")
        except UnicodeDecodeError:
            code = bytes()

        tree = get_parser(TreeSitterParser.PARSERS[file.language]).parse(code)
        return ASTParsedFile(
            file.path,
            file.language,
            code,
            list(TreeSitterParser.traverse_tree(tree.root_node, types))
        )

    return tokenize_files


def unzip_nodes(file: ASTParsedFile) -> List[ASTNode]:
    """
    Return list of nodes from parsed file

    :param file: parsed file instance with nodes
    :return: list of nodes from file
    """
    return [ASTNode(node, file) for node in file.nodes]


# TODO: That wrapping list is weird
def build_identifiers_extractor(subtokenize: bool = False) -> IdentifiersExtractor:
    """
    Build identifiers extractor to extract identifiers from parsed node

    :param subtokenize: if True will split tokens into subtokens otherwise return tokens as is
    :return: function to extract identifiers from node
    """
    def extractor(node: ASTNode) -> IdentifiersParsedNode:
        """
        Extract identifiers for given node

        :param node: node with identifiers
        :return: node with parsed identifiers
        """
        base_extractor = TreeSitterParser.get_identifier_from_node
        if subtokenize:
            identifiers = subtokenize_identifier(base_extractor(node.file.code, node.node))
        else:
            identifiers = [base_extractor(node.file.code, node.node)]
        return IdentifiersParsedNode(node.file.path, identifiers)

    return extractor


def build_objects_extractor(lang: str, object_type: ObjectTypes, subtokenize: bool = False) -> ObjectsExtractor:
    """
    Build objects extractor from node

    # TODO: Infer programming language somehow
    :param lang: programming language used for extraction
    :param object_type: type of object to extract
    :param subtokenize: if True object indetifiers come subtokenized otherwise the whole identifier is returned
    """

    def extractor(node: ASTNode) -> ObjectsParsedNode:
        """
        Extract object from given node

        :param node: node to extract objects from
        :return: parsed object from node
        """
        obj = TreeSitterParser.get_object_from_node(object_type, node.file.code, node.node, lang, subtokenize)
        return ObjectsParsedNode(node.file.path, node.file.language, [obj])

    return extractor
