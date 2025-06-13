from jambo.parser import ObjectTypeParser, RefTypeParser

from unittest import TestCase


class TestRefTypeParser(TestCase):
    def test_ref_type_parser_with_def(self):
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
            "person",
            properties,
            context=properties,
            ref_cache={},
            required=True,
        )

        self.assertIsInstance(type_parsing, type)

        obj = type_parsing(name="John", age=30)

        self.assertEqual(obj.name, "John")
        self.assertEqual(obj.age, 30)

    def test_ref_type_parser_with_forward_ref(self):
        properties = {
            "title": "person",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "emergency_contact": {
                    "$ref": "#",
                },
            },
            "required": ["name", "age"],
        }

        model, type_validator = ObjectTypeParser().from_properties(
            "person",
            properties,
            context=properties,
            ref_cache={},
            required=True,
        )

        obj = model(
            name="John",
            age=30,
            emergency_contact=model(
                name="Jane",
                age=28,
            ),
        )

        self.assertEqual(obj.name, "John")
        self.assertEqual(obj.age, 30)
        self.assertIsInstance(obj.emergency_contact, model)
        self.assertEqual(obj.emergency_contact.name, "Jane")
        self.assertEqual(obj.emergency_contact.age, 28)

    def test_ref_type_parser_forward_ref_can_checks_validation(self):
        properties = {
            "title": "person",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "emergency_contact": {
                    "$ref": "#",
                },
            },
            "required": ["name", "age"],
        }

        model, type_validator = ObjectTypeParser().from_properties(
            "person",
            properties,
            context=properties,
            ref_cache={},
            required=True,
        )

        # checks if when created via FowardRef the model is validated correctly.
        with self.assertRaises(ValueError):
            model(
                name="John",
                age=30,
                emergency_contact=model(
                    name="Jane",
                ),
            )

    def test_ref_type_parser_with_ciclic_def(self):
        properties = {
            "title": "person",
            "$ref": "#/$defs/person",
            "$defs": {
                "person": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer"},
                        "emergency_contact": {
                            "$ref": "#/$defs/person",
                        },
                    },
                }
            },
        }

        model, type_validator = RefTypeParser().from_properties(
            "person",
            properties,
            context=properties,
            ref_cache={},
            required=True,
        )

        obj = model(
            name="John",
            age=30,
            emergency_contact=model(
                name="Jane",
                age=28,
            ),
        )

        self.assertEqual(obj.name, "John")
        self.assertEqual(obj.age, 30)
        self.assertIsInstance(obj.emergency_contact, model)
        self.assertEqual(obj.emergency_contact.name, "Jane")
        self.assertEqual(obj.emergency_contact.age, 28)
