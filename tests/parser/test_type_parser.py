from jambo.parser._type_parser import GenericTypeParser

from typing import Any
from unittest import TestCase


class InvalidGenericTypeParser(GenericTypeParser):
    mapped_type = str
    json_schema_type = "invalid"

    def from_properties(
        self, name: str, properties: dict[str, Any], required: bool = False
    ): ...


class TestGenericTypeParser(TestCase):
    def test_invalid_get_impl(self):
        # Assuming GenericTypeParser is imported from the module
        with self.assertRaises(ValueError):
            GenericTypeParser.type_from_properties(
                "placeholder", {"type": "another_invalid_type"}
            )

    def test_invalid_json_schema_type(self):
        InvalidGenericTypeParser.json_schema_type = None

        # This is more for the developer's sanity check
        with self.assertRaises(RuntimeError):
            GenericTypeParser.type_from_properties(
                "placeholder", {"type": "another_invalid_type"}
            )

    def test_invalid_mappings_properties_builder(self):
        parser = InvalidGenericTypeParser()
        with self.assertRaises(NotImplementedError):
            parser.mappings_properties_builder({}, required=False)
