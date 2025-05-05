from jambo.parser._type_parser import GenericTypeParser

from typing import ClassVar


class StringTypeParser(GenericTypeParser):
    mapped_type = str

    json_schema_type = "type:string"

    type_mappings: ClassVar[dict[str, str]] = {  # type: ignore
        "maxLength": "max_length",
        "minLength": "min_length",
        "pattern": "pattern",
    }

    def from_properties(self, name, properties, required=False, **kwargs):
        mapped_properties = self.mappings_properties_builder(properties, required)

        default_value = properties.get("default")
        if default_value is not None:
            self.validate_default(str, mapped_properties, default_value)

        return str, mapped_properties
