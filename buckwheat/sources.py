import os
import tempfile
from typing import List

from buckwheat.tokenizer import recognize_languages_dir
from buckwheat.types import LanguageClassifiedFile, Repository, ProgrammingLanguages
from buckwheat.utils import clone_repository


# TODO: Should be done with hydra.cc
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


def transform_repository_to_files(repository: Repository) -> List[LanguageClassifiedFile]:
    """
    Transform repository to list of files with programming language specified

    :param repository: repository instance
    :return: list of files with programming languages
    """
    return [
        LanguageClassifiedFile(os.path.join(repository.path, file), ProgrammingLanguages(lang))
        for lang, files in repository.language_file_index.items()
        for file in files
    ]
