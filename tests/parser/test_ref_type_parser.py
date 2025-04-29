from jambo.parser.ref_type_parser import RefTypeParser

from unittest import TestCase


class TestRefTypeParser(TestCase):
    def test_parse_ref_type(self):
        properties = {
            "title": "person",
            "$ref": "#/$defs/person",
            "$defs": {
                "person": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer"},
                    },
                }
            },
        }

        type_parsing, type_validator = RefTypeParser().from_properties(
            properties=properties,
            name="placeholder",
            context=properties,
            required=True,
        )

        self.assertIsInstance(type_parsing, type)

        obj = type_parsing(name="John", age=30)

        self.assertEqual(obj.name, "John")
        self.assertEqual(obj.age, 30)

    def test_parser_ref_type_recursive(self):
        properties = {
            "title": "person",
            "$ref": "#/$defs/person",
            "$defs": {
                "person": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer"},
                        "friends": {
                            "type": "array",
                            "items": {"$ref": "#/$defs/person"},
                        },
                    },
                }
            },
        }

        type_parsing, type_validator = RefTypeParser().from_properties(
            properties=properties,
            name="placeholder",
            context=properties,
            required=True,
        )

        self.assertIsInstance(type_parsing, type)

        obj = type_parsing(name="John", age=30, friends=[{"name": "Doe", "age": 25}])

        self.assertEqual(obj.name, "John")
        self.assertEqual(obj.age, 30)
        self.assertEqual(len(obj.friends), 1)
        self.assertEqual(obj.friends[0].name, "Doe")
