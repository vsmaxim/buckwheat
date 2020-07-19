from itertools import chain

import pygments

TREE_SITTER_IDENTIFIERS = {"JavaScript": {"identifier", "property_identifier",
                                          "shorthand_property_identifier"},
                           "Python": {"identifier"},
                           "Java": {"identifier", "type_identifier"},
                           "Go": {"identifier", "field_identifier", "type_identifier"},
                           "C++": {"identifier", "namespace_identifier", "field_identifier",
                                   "type_identifier"},
                           "Ruby": {"identifier", "constant", "symbol"},
                           "TypeScript": {"identifier", "property_identifier",
                                          "shorthand_property_identifier", "type_identifier"},
                           "TSX": {"identifier", "property_identifier",
                                   "shorthand_property_identifier", "type_identifier"},
                           "PHP": {"name"},
                           "C#": {"identifier"},
                           "C": {"identifier", "field_identifier", "type_identifier"},
                           "Shell": {"variable_name", "command_name"},
                           "Rust": {"identifier", "field_identifier", "type_identifier"}}

PYGMENTS_IDENTIFIERS = {"Scala": {pygments.token.Name, pygments.token.Keyword.Type},
                        "Swift": {pygments.token.Name},
                        "Kotlin": {pygments.token.Name},
                        "Haskell": {pygments.token.Name, pygments.token.Keyword.Type}}

IDENTIFIER_TYPES = set(
    identifier
    for identifiers in chain(
        TREE_SITTER_IDENTIFIERS.values(),
        PYGMENTS_IDENTIFIERS.values(),
    )
    for identifier in identifiers
)
