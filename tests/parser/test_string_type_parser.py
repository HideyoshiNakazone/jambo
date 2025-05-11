from jambo.parser import StringTypeParser

from pydantic import EmailStr, HttpUrl, IPvAnyAddress

from datetime import date, datetime, time
from unittest import TestCase


class TestStringTypeParser(TestCase):
    def test_string_parser_no_options(self):
        parser = StringTypeParser()

        properties = {"type": "string"}

        type_parsing, type_validator = parser.from_properties("placeholder", properties)

        self.assertEqual(type_parsing, str)

    def test_string_parser_with_options(self):
        parser = StringTypeParser()

        properties = {
            "type": "string",
            "maxLength": 10,
            "minLength": 1,
            "pattern": "^[a-zA-Z]+$",
        }

        type_parsing, type_validator = parser.from_properties("placeholder", properties)

        self.assertEqual(type_parsing, str)
        self.assertEqual(type_validator["max_length"], 10)
        self.assertEqual(type_validator["min_length"], 1)
        self.assertEqual(type_validator["pattern"], "^[a-zA-Z]+$")

    def test_string_parser_with_default_value(self):
        parser = StringTypeParser()

        properties = {
            "type": "string",
            "default": "default_value",
            "maxLength": 20,
            "minLength": 5,
        }

        type_parsing, type_validator = parser.from_properties("placeholder", properties)

        self.assertEqual(type_parsing, str)
        self.assertEqual(type_validator["default"], "default_value")
        self.assertEqual(type_validator["max_length"], 20)
        self.assertEqual(type_validator["min_length"], 5)

    def test_string_parser_with_invalid_default_value_type(self):
        parser = StringTypeParser()

        properties = {
            "type": "string",
            "default": 12345,  # Invalid default value
            "maxLength": 20,
            "minLength": 5,
        }

        with self.assertRaises(ValueError):
            parser.from_properties("placeholder", properties)

    def test_string_parser_with_default_invalid_maxlength(self):
        parser = StringTypeParser()

        properties = {
            "type": "string",
            "default": "default_value",
            "maxLength": 2,
            "minLength": 1,
        }

        with self.assertRaises(ValueError):
            parser.from_properties("placeholder", properties)

    def test_string_parser_with_default_invalid_minlength(self):
        parser = StringTypeParser()

        properties = {
            "type": "string",
            "default": "a",
            "maxLength": 20,
            "minLength": 2,
        }

        with self.assertRaises(ValueError):
            parser.from_properties("placeholder", properties)

    def test_string_parser_with_email_format(self):
        parser = StringTypeParser()

        properties = {
            "type": "string",
            "format": "email",
        }

        type_parsing, type_validator = parser.from_properties("placeholder", properties)

        self.assertEqual(type_parsing, EmailStr)

    def test_string_parser_with_uri_format(self):
        parser = StringTypeParser()

        properties = {
            "type": "string",
            "format": "uri",
        }

        type_parsing, type_validator = parser.from_properties("placeholder", properties)

        self.assertEqual(type_parsing, HttpUrl)

    def test_string_parser_with_ip_formats(self):
        parser = StringTypeParser()

        for ip_format in ["ipv4", "ipv6"]:
            properties = {
                "type": "string",
                "format": ip_format,
            }

            type_parsing, type_validator = parser.from_properties(
                "placeholder", properties
            )

            self.assertEqual(type_parsing, IPvAnyAddress)

    def test_string_parser_with_time_format(self):
        parser = StringTypeParser()

        properties = {
            "type": "string",
            "format": "time",
        }

        type_parsing, type_validator = parser.from_properties("placeholder", properties)

        self.assertEqual(type_parsing, time)

    def test_string_parser_with_pattern_based_formats(self):
        parser = StringTypeParser()

        for format_type in ["hostname"]:
            properties = {
                "type": "string",
                "format": format_type,
            }

            type_parsing, type_validator = parser.from_properties(
                "placeholder", properties
            )

            self.assertEqual(type_parsing, str)
            self.assertIn("pattern", type_validator)
            self.assertEqual(
                type_validator["pattern"], parser.format_pattern_mapping[format_type]
            )

    def test_string_parser_with_unsupported_format(self):
        parser = StringTypeParser()

        properties = {
            "type": "string",
            "format": "unsupported-format",
        }

        with self.assertRaises(ValueError) as context:
            parser.from_properties("placeholder", properties)

        self.assertEqual(
            str(context.exception), "Unsupported string format: unsupported-format"
        )

    def test_string_parser_with_date_format(self):
        parser = StringTypeParser()

        properties = {
            "type": "string",
            "format": "date",
        }

        type_parsing, type_validator = parser.from_properties("placeholder", properties)

        self.assertEqual(type_parsing, date)

    def test_string_parser_with_datetime_format(self):
        parser = StringTypeParser()

        properties = {
            "type": "string",
            "format": "date-time",
        }

        type_parsing, type_validator = parser.from_properties("placeholder", properties)

        self.assertEqual(type_parsing, datetime)
