from jambo.parser.anyof_type_parser import AnyOfTypeParser

from typing import Annotated, Union, get_args, get_origin
from unittest import TestCase


class TestAnyOfTypeParser(TestCase):
    def test_any_with_missing_properties(self):
        properties = {
            "notAnyOf": [
                {"type": "string"},
                {"type": "integer"},
            ],
        }

        with self.assertRaises(ValueError):
            AnyOfTypeParser().from_properties("placeholder", properties)

    def test_any_of_with_invalid_properties(self):
        properties = {
            "anyOf": None,
        }

        with self.assertRaises(ValueError):
            AnyOfTypeParser().from_properties("placeholder", properties)

    def test_any_of_string_or_int(self):
        """
        Tests the AnyOfTypeParser with a string or int type.
        """

        properties = {
            "anyOf": [
                {"type": "string"},
                {"type": "integer"},
            ],
        }

        type_parsing, _ = AnyOfTypeParser().from_properties(
            "placeholder", properties, required=True
        )

        # check union type has string and int
        self.assertEqual(get_origin(type_parsing), Union)

        type_1, type_2 = get_args(type_parsing)

        self.assertEqual(get_origin(type_1), Annotated)
        self.assertIn(str, get_args(type_1))

        self.assertEqual(get_origin(type_2), Annotated)
        self.assertIn(int, get_args(type_2))

    def test_any_of_string_or_int_with_default(self):
        """
        Tests the AnyOfTypeParser with a string or int type and a default value.
        """

        properties = {
            "anyOf": [
                {"type": "string"},
                {"type": "integer"},
            ],
            "default": 42,
        }

        type_parsing, type_validator = AnyOfTypeParser().from_properties(
            "placeholder", properties
        )

        # check union type has string and int
        self.assertEqual(get_origin(type_parsing), Union)

        type_1, type_2 = get_args(type_parsing)

        self.assertEqual(get_origin(type_1), Annotated)
        self.assertIn(str, get_args(type_1))

        self.assertEqual(get_origin(type_2), Annotated)
        self.assertIn(int, get_args(type_2))

        self.assertEqual(type_validator["default"], 42)

    def test_any_string_or_int_with_invalid_defaults(self):
        """
        Tests the AnyOfTypeParser with a string or int type and an invalid default value.
        """  # noqa: E501

        properties = {
            "anyOf": [
                {"type": "string"},
                {"type": "integer"},
            ],
            "default": 3.14,
        }

        with self.assertRaises(ValueError):
            AnyOfTypeParser().from_properties("placeholder", properties)
