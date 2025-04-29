from jambo.parser._type_parser import GenericTypeParser


class ObjectTypeParser(GenericTypeParser):
    mapped_type = object

    json_schema_type = "type:object"

    @staticmethod
    def from_properties(name, properties, **kwargs):
        from jambo.schema_converter import SchemaConverter

        type_parsing = SchemaConverter.build_object(name, properties, **kwargs)
        type_properties = {}

        if "default" in properties:
            type_properties["default_factory"] = lambda: type_parsing.model_validate(
                properties["default"]
            )

        return type_parsing, type_properties
