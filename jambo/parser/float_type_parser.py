from jambo.parser._type_parser import GenericTypeParser


class FloatTypeParser(GenericTypeParser):
    mapped_type = float

    json_schema_type = "type:number"

    type_mappings = {
        "minimum": "ge",
        "exclusiveMinimum": "gt",
        "maximum": "le",
        "exclusiveMaximum": "lt",
        "multipleOf": "multiple_of",
        "default": "default",
    }

    def from_properties(self, name, properties, required=False):
        mapped_properties = self.mappings_properties_builder(properties, required)

        default_value = mapped_properties.get("default")
        if default_value is not None:
            self.validate_default(float, mapped_properties, default_value)

        return float, mapped_properties
