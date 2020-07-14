import os
import tempfile
from typing import List

from buckwheat.tokenizer import recognize_languages_dir
from buckwheat.types import LanguageClassifiedFile, Repository
from buckwheat.utils import clone_repository


# TODO: Probably should be done with hydra.cc
def get_repositories_list(repositories_file: str) -> List[str]:
    """
    Parse list of repositories from input file

    :param repositories_file: file containing repositories list
    :return: list of repositories links
    """
    with open(repositories_file, "r") as reps:
        repositories = reps.read().splitlines()
    return repositories


def get_repository_instance(repository_link: str) -> Repository:
    """
    Construct repository instance and create all needed folders for parsing

    :param repository_link: link of repository
    :return: repository instance
    """
    temp_directory = tempfile.mkdtemp()
    clone_repository(repository_link, temp_directory)
    return Repository(temp_directory, recognize_languages_dir(temp_directory))


def build_language_filter(target_language: str):
    """
    Build function to filter files with given programming language

    :param target_languages: language to filter against
    :return: filter function
    """
    def inner_filter(file: LanguageClassifiedFile) -> bool:
        """Return True if file.language is target language otherwise return False"""
        return file.language == target_language

    return inner_filter


def build_file_transformer():
    """
    Build function to transform repository instance to list of files with programming languages specified

    :return: transform function
    """
    def transform_repository_to_files(repository: Repository) -> List[LanguageClassifiedFile]:
        """
        Transform repository to list of files with programming language specified

        :param repository: repository instance
        :return: list of files with programming languages
        """
        return [
            LanguageClassifiedFile(os.path.join(repository.path, file), lang)
            for lang, files in repository.language_file_index.items()
            for file in files
        ]

    return transform_repository_to_files
