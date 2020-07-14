"""
Subtokenizing-related tests.
"""
from typing import List

import pytest

from buckwheat.subtokenizer import TokenParser

tokenizer = TokenParser()


@pytest.mark.parametrize("token,actual_subtokens", [
    ["token", ["token"]],
    ["Upper", ["upper"]],
    ["camelCase", ["camel", "case"]],
    ["snake_case", ["snake", "case"]],
    ["os", []],
    ["wdSize", ["size", "wdsize"]],
    ["Egor.is.Nice", ["egor", "nice", "isnice"]],
    ["stemming", ["stem"]],
    ["sourced_directory", ["sourc", "directori"]],
    ["some.ABSUrdSpecific_case.ml.in.code", ["some", "abs", "urd", "specif", "case", "code", "incode"]]
])
def test_subtokenizer(token: str, actual_subtokens: List[str]):
    subtokens = list(tokenizer.process_token(token))
    assert subtokens == actual_subtokens
