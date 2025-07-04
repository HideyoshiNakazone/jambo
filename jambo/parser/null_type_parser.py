from jambo.parser._type_parser import GenericTypeParser
from jambo.types.type_parser_options import TypeParserOptions

from typing_extensions import Unpack


class NullTypeParser(GenericTypeParser):
    mapped_type = None

    json_schema_type = "type:null"

    type_mappings = {
        "default": "default",
    }

    def from_properties_impl(
        self, name, properties, **kwargs: Unpack[TypeParserOptions]
    ):
        mapped_properties = self.mappings_properties_builder(properties, **kwargs)

        default_value = properties.get("default")
        if default_value is not None:
            raise ValueError(f"Default value for {name} must be None.")

        return None, mapped_properties
