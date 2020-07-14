from pathlib import Path

from dask import bag

from buckwheat.extractors import build_nodes_extractor, unzip_nodes, build_identifiers_extractor
from buckwheat.sources import get_repositories_list, get_repository_instance, build_language_filter, \
    build_file_transformer
from buckwheat.tokenizer import TreeSitterParser
from buckwheat.transformers import build_identifiers_to_vawbit_transformer
from buckwheat.utils import build_node_filter, reduce_to_tuple, ProgrammingLanguages

BASE_DIR = Path(__file__).parent.parent

INPUT_FILE = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

if __name__ == "__main__":
    language = ProgrammingLanguages.PYTHON.value
    node_types = TreeSitterParser.CLASSES[language]

    transform_repo_to_file = build_file_transformer()
    is_needed_language = build_language_filter(language)
    extract_nodes = build_nodes_extractor(node_types)
    is_needed_node_type = build_node_filter(node_types)
    extract_identifiers = build_identifiers_extractor(subtokenize=True)
    transform_to_vawbit = build_identifiers_to_vawbit_transformer(verbose=True)

    repo_bag = bag.from_sequence(get_repositories_list(INPUT_FILE))

    first_n_objects = (
        repo_bag.map(get_repository_instance)
                .map(transform_repo_to_file)
                .flatten()
                .filter(is_needed_language)
                .map(extract_nodes)
                .map(unzip_nodes)
                .flatten()
                .filter(is_needed_node_type)
                .map(extract_identifiers)
                .foldby(lambda i: i.file, reduce_to_tuple, tuple())
                .map(lambda tpl: tpl[1])
                .map(transform_to_vawbit)
                .to_textfiles(str(OUTPUT_DIR / "parsed-vawbit-*"))
    )

    print(first_n_objects)
