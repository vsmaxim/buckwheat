"""
Pipeline-related tests.
"""
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from dask import bag

from buckwheat.extractors import build_nodes_extractor, build_identifiers_extractor, unzip_nodes
from buckwheat.sources import build_file_transformer, build_language_filter
from buckwheat.types import Repository
from buckwheat.tokenizer import recognize_languages_dir, tokenize_list_of_repositories, transform_files_list, \
    TreeSitterParser
from buckwheat.transformers import build_identifiers_to_vawbit_transformer
from buckwheat.utils import build_node_filter, ProgrammingLanguages, reduce_to_tuple

TESTS_DIR = Path(__file__).parent
PROGRAMMING_LANGUAGES = {"C", "C#", "C++", "Go", "Haskell", "Java", "JavaScript", "Kotlin", "PHP", "Python", "Ruby",
                         "Rust", "Scala", "Shell", "Swift", "TypeScript"}


def test_languages():
    lang2files = recognize_languages_dir(os.path.abspath(os.path.join(TESTS_DIR, "test_files")))
    assert lang2files.keys() == PROGRAMMING_LANGUAGES


def test_tokenization():
    input_file = TESTS_DIR / "test_files" / "test.txt"

    with TemporaryDirectory() as td:
        output_file = Path(td) / "wabbit_counters_files_0.txt"
        tokenize_list_of_repositories(input_file, td, 100, "counters", "files", None, True, "wabbit",
                                      identifiers_verbose=False, subtokenize=True)

        wabbit_lines = len(open(output_file).readlines())
        assert wabbit_lines == 16


def test_transforming_list():
    lang2files = recognize_languages_dir(str(TESTS_DIR / "test_files"))
    files = transform_files_list(lang2files, "projects", None)
    assert len(files) == 16


def test_sample_pipeline_with_dask():
    # Functions to build pipeline
    language = ProgrammingLanguages.PYTHON.value
    node_types = TreeSitterParser.CLASSES[language]

    transform_repo_to_file = build_file_transformer()
    is_needed_language = build_language_filter(language)
    extract_nodes = build_nodes_extractor(node_types)
    is_needed_node_type = build_node_filter(node_types)
    extract_identifiers = build_identifiers_extractor(subtokenize=True)
    transform_to_vawbit = build_identifiers_to_vawbit_transformer(verbose=True)

    test_languages_dir = str(TESTS_DIR / "test_files")
    test_repository_instance = Repository(test_languages_dir, recognize_languages_dir(test_languages_dir))

    repo_bag = bag.from_sequence([test_repository_instance])

    first_n_objects = (
        repo_bag.map(transform_repo_to_file)
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
                .take(10)
    )

    assert len(first_n_objects) == 10
