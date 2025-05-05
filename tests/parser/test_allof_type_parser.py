from jambo.parser.allof_type_parser import AllOfTypeParser

from unittest import TestCase


class TestAllOfTypeParser(TestCase):
    def test_all_of_type_parser_object_type(self):
        """
        Test the AllOfTypeParser with an object type and validate the properties.
        When using allOf with object it should be able to validate the properties
        and join them correctly.
        """
        properties = {
            "type": "object",
            "allOf": [
                {
                    "properties": {
                        "name": {
                            "type": "string",
                            "minLength": 1,
                        }
                    },
                },
                {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "maxLength": 4,
                        },
                        "age": {
                            "type": "integer",
                            "maximum": 100,
                            "minimum": 0,
                        },
                    },
                },
            ],
        }

        type_parsing, type_validator = AllOfTypeParser().from_properties(
            "placeholder", properties
        )

        with self.assertRaises(ValueError):
            type_parsing(name="John", age=101)

        with self.assertRaises(ValueError):
            type_parsing(name="", age=30)

        with self.assertRaises(ValueError):
            type_parsing(name="John Invalid", age=30)

        obj = type_parsing(name="John", age=30)
        self.assertEqual(obj.name, "John")
        self.assertEqual(obj.age, 30)

    def test_all_of_type_parser_object_type_required(self):
        """
        Tests the required properties of the AllOfTypeParser with an object type.
        """

        properties = {
            "type": "object",
            "allOf": [
                {
                    "properties": {
                        "name": {
                            "type": "string",
                        }
                    },
                    "required": ["name"],
                },
                {
                    "type": "object",
                    "properties": {
                        "age": {
                            "type": "integer",
                        }
                    },
                    "required": ["age"],
                },
            ],
        }

        type_parsing, type_validator = AllOfTypeParser().from_properties(
            "placeholder", properties
        )

        with self.assertRaises(ValueError):
            type_parsing(name="John")

        with self.assertRaises(ValueError):
            type_parsing(age=30)

        obj = type_parsing(name="John", age=30)
        self.assertEqual(obj.name, "John")
        self.assertEqual(obj.age, 30)

    def test_all_of_type_top_level_type(self):
        """
        Tests the AllOfTypeParser with a top-level type and validate the properties.
        """

        properties = {
            "type": "string",
            "allOf": [
                {"maxLength": 11},
                {"maxLength": 4},
                {"minLength": 1},
                {"minLength": 2},
            ],
        }

        type_parsing, type_validator = AllOfTypeParser().from_properties(
            "placeholder", properties
        )

        self.assertEqual(type_parsing, str)
        self.assertEqual(type_validator["max_length"], 11)
        self.assertEqual(type_validator["min_length"], 1)

    def test_all_of_type_parser_in_fields(self):
        """
        Tests the AllOfTypeParser when set in the fields of a model.
        """
        properties = {
            "allOf": [
                {"type": "string", "maxLength": 11},
                {"type": "string", "maxLength": 4},
                {"type": "string", "minLength": 1},
                {"type": "string", "minLength": 2},
            ]
        }

        type_parsing, type_validator = AllOfTypeParser().from_properties(
            "placeholder", properties
        )

        self.assertEqual(type_parsing, str)
        self.assertEqual(type_validator["max_length"], 11)
        self.assertEqual(type_validator["min_length"], 1)

    def test_invalid_all_of(self):
        """
        Tests that an error is raised when the allOf type is not present.
        """
        properties = {
            "wrongKey": [
                {"type": "string", "maxLength": 11},
                {"type": "string", "maxLength": 4},
                {"type": "string", "minLength": 1},
                {"type": "string", "minLength": 2},
            ]
        }

        with self.assertRaises(ValueError):
            AllOfTypeParser().from_properties("placeholder", properties)

    def test_all_of_invalid_type_not_present(self):
        properties = {
            "allOf": [
                {"maxLength": 11},
                {"maxLength": 4},
                {"minLength": 1},
                {"minLength": 2},
            ]
        }

        with self.assertRaises(ValueError):
            AllOfTypeParser().from_properties("placeholder", properties)

    def test_all_of_invalid_type_in_fields(self):
        properties = {
            "allOf": [
                {"type": "string", "maxLength": 11},
                {"type": "integer", "maxLength": 4},
                {"type": "string", "minLength": 1},
                {"minLength": 2},
            ]
        }

        with self.assertRaises(ValueError):
            AllOfTypeParser().from_properties("placeholder", properties)

    def test_all_of_description_field(self):
        """
        Tests the AllOfTypeParser with a description field.
        """

        properties = {
            "type": "object",
            "allOf": [
                {
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "One",
                        }
                    },
                },
                {
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Of",
                        }
                    },
                },
                {
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Us",
                        }
                    },
                },
            ],
        }

        type_parsing, _ = AllOfTypeParser().from_properties("placeholder", properties)

        self.assertEqual(
            type_parsing.model_json_schema()["properties"]["name"]["description"],
            "One | Of | Us",
        )

    def test_all_of_with_defaults(self):
        """
        Tests the AllOfTypeParser with a default value.
        """

        properties = {
            "type": "object",
            "allOf": [
                {
                    "properties": {
                        "name": {
                            "type": "string",
                            "default": "John",
                        }
                    },
                },
                {
                    "properties": {
                        "name": {
                            "type": "string",
                            "default": "John",
                        },
                        "age": {
                            "type": "integer",
                            "default": 30,
                        },
                    },
                },
            ],
        }

        type_parsing, _ = AllOfTypeParser().from_properties("placeholder", properties)
        obj = type_parsing()
        self.assertEqual(obj.name, "John")
        self.assertEqual(obj.age, 30)

    def test_all_of_with_conflicting_defaults(self):
        """
        Tests the AllOfTypeParser with conflicting default values.
        """

        properties = {
            "type": "object",
            "allOf": [
                {
                    "properties": {
                        "name": {
                            "type": "string",
                            "default": "John",
                        }
                    },
                },
                {
                    "properties": {
                        "name": {
                            "type": "string",
                            "default": "Doe",
                        }
                    },
                },
            ],
        }

        with self.assertRaises(ValueError):
            AllOfTypeParser().from_properties("placeholder", properties)
