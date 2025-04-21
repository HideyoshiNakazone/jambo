from jambo.parser._type_parser import GenericTypeParser

from unittest import TestCase


class TestGenericTypeParser(TestCase):
    def setUp(self):
        # Create a subclass of GenericTypeParser for testing
        # Made locally to avoid polluting the global namespace
        class InvalidGenericTypeParser(GenericTypeParser):
            mapped_type = str
            json_schema_type = "invalid"

            def from_properties(
                self, name: str, properties: dict[str, any], required: bool = False
            ): ...

        self.InvalidGenericTypeParser = InvalidGenericTypeParser

    def tearDown(self):
        # Clean up the InvalidGenericTypeParser class
        del self.InvalidGenericTypeParser

    def test_invalid_get_impl(self):
        # Assuming GenericTypeParser is imported from the module
        with self.assertRaises(ValueError):
            GenericTypeParser._get_impl({"invalid_type": "invalid"})

    def test_invalid_json_schema_type(self):
        self.InvalidGenericTypeParser.json_schema_type = None

        # This is more for the developer's sanity check
        with self.assertRaises(RuntimeError):
            GenericTypeParser._get_impl({"invalid_type": "invalid"})

    def test_invalid_mappings_properties_builder(self):
        parser = self.InvalidGenericTypeParser()
        with self.assertRaises(NotImplementedError):
            parser.mappings_properties_builder({}, required=False)
