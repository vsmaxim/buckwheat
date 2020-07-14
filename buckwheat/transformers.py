from typing import Tuple, Generator, Callable

from buckwheat.types import IdentifiersParsedNode, IdentifierData


def build_identifiers_to_vawbit_transformer(verbose: bool = True) -> Callable[[Tuple[IdentifiersParsedNode, ...]], str]:
    """
    Build function to transform parsed nodes into vowpal wabbit format
    More information about format can be found at https://github.com/VowpalWabbit/vowpal_wabbit/wiki/Input-format

    :param verbose: If True verbose format representation used otherwise plain identifiers are used
    :return: transformer function
    """

    def map_to_identifiers(identifier_nodes: Tuple[IdentifiersParsedNode, ...]) -> Generator[IdentifierData, None, None]:
        """
        Make generator yielding identifiers from sequence of parsed nodes.

        :param identifier_nodes: sequence of parsed identifier nodes
        :return: generator with separate identifiers from nodes
        """
        for node in identifier_nodes:
            for identifier in node.identifiers:
                yield identifier

    def identifiers_to_vawbit(nodes: Tuple[IdentifiersParsedNode, ...]) -> str:
        """
        Construct compact vowpal wabbit string representation from list of parsed nodes, filename of representation is
        the first node file path.

        :param nodes: list of parsed nodes from file
        :return: compact string representation of file
        """
        filename = nodes[0].file
        identifiers_string = " ".join([i.identifier for i in map_to_identifiers(nodes)])
        return f"{filename} {identifiers_string}"

    def verbose_identifiers_to_vawbit(nodes: Tuple[IdentifiersParsedNode, ...]) -> str:
        """
        Construct verbose vowpal wabbit string representation from list of parsed nodes, filename of representation is
        the first node file path.

        :param nodes: list of parsed nodes from file
        :return: verbose string representation of file
        """
        filename = nodes[0].file
        identifier_generator = map_to_identifiers(nodes)
        identifiers_string = " ".join([
            f"{i.identifier}:{i.start_byte},{i.start_line},{i.start_column}"
            for i in identifier_generator
        ])
        return f"{filename} {identifiers_string}"

    if verbose:
        return verbose_identifiers_to_vawbit

    return identifiers_to_vawbit
