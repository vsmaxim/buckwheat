from typing import Tuple, Callable, List

from buckwheat.types import LanguageClassifiedFile, Entity

FileEntitiesPair = Tuple[LanguageClassifiedFile, List[Entity]]


def build_identifiers_to_vawbit_transformer(verbose: bool = True) -> Callable[[FileEntitiesPair], str]:
    """
    Build function to transform parsed nodes into vowpal wabbit format
    More information about format can be found at https://github.com/VowpalWabbit/vowpal_wabbit/wiki/Input-format

    :param verbose: If True verbose format representation used otherwise plain identifiers are used
    :return: transformer function
    """

    def identifiers_to_vawbit(file_with_entities: FileEntitiesPair) -> str:
        """
        Construct compact vowpal wabbit string representation from list of parsed nodes, filename of representation is
        the first node file path.

        :param nodes: list of parsed nodes from file
        :return: compact string representation of file
        """
        file, entities = file_with_entities
        identifiers_string = " ".join([entity.vowpal_compact_format for entity in entities])
        return f"{file.path} {identifiers_string}"

    def verbose_identifiers_to_vawbit(file_with_entities: FileEntitiesPair) -> str:
        """
        Construct verbose vowpal wabbit string representation from list of parsed nodes, filename of representation is
        the first node file path.

        :param nodes: list of parsed nodes from file
        :return: verbose string representation of file
        """
        file, entities = file_with_entities
        identifiers_string = " ".join([entity.vowpal_verbose_format for entity in entities])
        return f"{file.path} {identifiers_string}"

    if verbose:
        return verbose_identifiers_to_vawbit

    return identifiers_to_vawbit
