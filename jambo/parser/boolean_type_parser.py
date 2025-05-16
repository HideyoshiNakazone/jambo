from jambo.parser._type_parser import GenericTypeParser


class BooleanTypeParser(GenericTypeParser):
    mapped_type = bool

    json_schema_type = "type:boolean"

    type_mappings = {
        "default": "default",
    }

    def from_properties(self, name, properties, required=False):
        mapped_properties = self.mappings_properties_builder(properties, required)

        default_value = properties.get("default")
        if default_value is not None and not isinstance(default_value, bool):
            raise ValueError(f"Default value for {name} must be a boolean.")

        return bool, mapped_properties
