from itertools import chain
from pathlib import Path
from typing import Dict, Set, List, Tuple

from dask import bag

from buckwheat.tokenizers import build_entities_extractor, TreeSitterExtractor, get_tree_sitter_spec, \
    get_pygments_extractor_spec
from buckwheat.sources import transform_repository_to_files, get_repositories_list, get_repository_instance
from buckwheat.tokenizer import TreeSitterParser, PygmentsParser
from buckwheat.types import Entity, ProgrammingLanguages


def get_files_bag(input_file: str) -> bag.Bag:
    return (
        bag.from_sequence(get_repositories_list(input_file))
           .map(get_repository_instance)
           .map(transform_repository_to_files)
           .flatten()
    )


def group_identifiers_by_parent_with_type(types: Set[str], identifiers: List[Entity]) -> List[Tuple[Entity, List[Entity]]]:
    def filter_entities_by_parent(parent_id) -> List[Entity]:
        filtered_entities = list(filter(lambda identifier: identifier[0].node_id == parent_id, identifiers_with_parents))
        parent_entities: List[Entity] = list(zip(*filtered_entities))[1]
        return parent_entities

    parent_identifiers = [entity.parent_of_type(types) for entity in identifiers]
    identifiers_with_parents = list(zip(parent_identifiers, identifiers))

    parents = {entity.node_id(): entity for entity in parent_identifiers}
    return [(parent, filter_entities_by_parent(parent_id)) for parent_id, parent in parents.items()]


def filter_identifiers_by_parent_type(types: Set[str], identifiers: List[Entity]):
    return [entity for entity in identifiers if entity.parent_of_type(types) is not None]


def get_files_with_identifiers_bag(input_file: str) -> bag.Bag:
    tree_sitter_extractors_spec = get_tree_sitter_spec(TreeSitterParser.IDENTIFIERS)
    pygments_extractors_spec = get_pygments_extractor_spec(PygmentsParser.IDENTIFIERS)

    extractors_spec = {**tree_sitter_extractors_spec, **pygments_extractors_spec}
    extractor = build_entities_extractor(extractors_spec)

    files_bag = get_files_bag(input_file)
    identifiers_bag = files_bag.map(extractor)

    return bag.zip(files_bag, identifiers_bag).filter(lambda pair: pair[1])


def get_classes_with_identifiers_bag(input_file: str) -> bag.Bag:
    extractors_spec = get_tree_sitter_spec(TreeSitterParser.IDENTIFIERS, TreeSitterParser.CLASSES)
    extractor = build_entities_extractor(extractors_spec)

    files_bag = get_files_bag(input_file)
    identifiers_bag = (
        files_bag.map(extractor)
                 .map(lambda i: filter_identifiers_by_parent_type(TreeSitterParser.CLASSES["Python"], i))
                 .map(lambda i: group_identifiers_by_parent_with_type(TreeSitterParser.CLASSES["Python"], i))
    )

    return bag.zip(files_bag, identifiers_bag).filter(lambda pair: pair[1])


def get_identifiers_for_custom_spec(input_file: str) -> bag.Bag:
    extract_specification = {
        ProgrammingLanguages.PYTHON: TreeSitterExtractor(
            ProgrammingLanguages.PYTHON,
            TreeSitterParser.IDENTIFIERS[ProgrammingLanguages.PYTHON.value],
            verbose=True,
        ),
        ProgrammingLanguages.C: TreeSitterExtractor(
            ProgrammingLanguages.C,
            TreeSitterParser.IDENTIFIERS[ProgrammingLanguages.PYTHON.value],
            verbose=True,
        ),
        ProgrammingLanguages.CSHARP: TreeSitterExtractor(
            ProgrammingLanguages.CSHARP,
            TreeSitterParser.IDENTIFIERS[ProgrammingLanguages.PYTHON.value],
            verbose=True,
        ),
    }

    extract_entities = build_entities_extractor(extract_specification)

    files_bag = get_files_bag(input_file)
    entities_bag = files_bag.map(extract_entities)
    return bag.zip(files_bag, entities_bag).filter(lambda pair: pair[1])


def sample_classes_extraction(input_file: str):
    classes_with_identifiers = get_classes_with_identifiers_bag(input_file).take(20)

    for file, parent_identifiers_pairs in classes_with_identifiers:
        print(f"File: {file.path}")

        for parent, identifiers in parent_identifiers_pairs:
            print(f"Parent: {parent.body} {parent.position.start_line}")
            print(f"Identifiers: {' '.join(identifier.body for identifier in identifiers)}\n")

        print("\n\n")


def sample_identifiers_extraction(input_file: str):
    files_with_identifiers = get_files_with_identifiers_bag(input_file).take(20)

    for file, identifiers in files_with_identifiers:
        print(f"File: {file.path}")
        print(f"Identifiers: {' '.join(identifier.body for identifier in identifiers)}")
        print()


def sample_identifiers_with_spec_extraction(input_file: str):
    files_with_identifiers = get_identifiers_for_custom_spec(input_file).take(20)

    for file, identifiers in files_with_identifiers:
        print(f"File: {file.path}")
        print(f"Identifiers: {' '.join(identifier.body for identifier in identifiers)}")
        print()


if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent
    input_file = str(base_dir / "input")

    sample_classes_extraction(input_file)
    # sample_identifiers_extraction(input_file)
    # sample_identifiers_with_spec_extraction(input_file)
