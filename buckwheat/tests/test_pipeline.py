"""
Pipeline-related tests.
"""
from itertools import chain
import os
from pathlib import Path

from buckwheat.tokenizer import recognize_languages_dir

TESTS_DIR = Path(__file__).parent
PROGRAMMING_LANGUAGES = {"C", "C#", "C++", "Go", "Haskell", "Java", "JavaScript", "Kotlin", "PHP", "Python", "Ruby",
                         "Rust", "Scala", "Shell", "Swift", "TypeScript"}


def test_languages():
    lang2files = recognize_languages_dir(os.path.abspath(os.path.join(TESTS_DIR, "test_files")))
    assert lang2files.keys() == PROGRAMMING_LANGUAGES


def test_recognize_languages():
    test_files_dir = TESTS_DIR / "test_files"
    languages = recognize_languages_dir(str(TESTS_DIR / "test_files"))
    assert languages.keys() == PROGRAMMING_LANGUAGES

    recognized_files_list = set(list(chain(*languages.values())))
    actual_files_list = set(map(lambda p: p.name, test_files_dir.glob("*")))
    assert recognized_files_list == actual_files_list
