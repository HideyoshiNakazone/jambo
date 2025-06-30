from jambo.parser import NullTypeParser

from unittest import TestCase


class TestNullTypeParser(TestCase):
    def test_null_parser_no_options(self):
        parser = NullTypeParser()

        properties = {"type": "null"}

        type_parsing, type_validator = parser.from_properties_impl(
            "placeholder", properties
        )

        self.assertEqual(type_parsing, None)
        self.assertEqual(type_validator, {"default": None})

    def test_null_parser_with_default(self):
        parser = NullTypeParser()

        properties = {
            "type": "null",
            "default": None,
        }

        type_parsing, type_validator = parser.from_properties_impl(
            "placeholder", properties
        )

        self.assertEqual(type_parsing, None)
        self.assertEqual(type_validator["default"], None)

    def test_null_parser_with_invalid_default(self):
        parser = NullTypeParser()

        properties = {
            "type": "null",
            "default": "invalid",
        }

        with self.assertRaises(ValueError):
            parser.from_properties_impl("placeholder", properties)
