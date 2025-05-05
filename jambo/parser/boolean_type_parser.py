from jambo.parser._type_parser import GenericTypeParser

from typing import ClassVar


class BooleanTypeParser(GenericTypeParser):
    mapped_type = bool

    json_schema_type = "type:boolean"

    type_mappings: ClassVar[dict[str, str]] = {  # type: ignore
        "default": "default",
    }

    def from_properties(self, name, properties, required=False, **kwargs):
        mapped_properties = self.mappings_properties_builder(properties, required)

        default_value = properties.get("default")
        if default_value is not None and not isinstance(default_value, bool):
            raise ValueError(f"Default value for {name} must be a boolean.")

        return bool, mapped_properties
