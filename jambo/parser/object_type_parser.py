from jambo.parser._type_parser import GenericTypeParser
from jambo.types.type_parser_options import TypeParserOptions

from pydantic import BaseModel, Field, create_model
from typing_extensions import Any, Unpack


class ObjectTypeParser(GenericTypeParser):
    mapped_type = object

    json_schema_type = "type:object"

    def from_properties_impl(
        self, name: str, properties: dict[str, Any], **kwargs: Unpack[TypeParserOptions]
    ) -> tuple[type[BaseModel], dict]:
        type_parsing = self.to_model(
            name,
            properties.get("properties", {}),
            properties.get("required", []),
            **kwargs,
        )
        type_properties = {}

        if "default" in properties:
            type_properties["default_factory"] = lambda: type_parsing.model_validate(
                properties["default"]
            )

        return type_parsing, type_properties

    @classmethod
    def to_model(
        cls,
        name: str,
        schema: dict[str, Any],
        required_keys: list[str],
        **kwargs: Unpack[TypeParserOptions],
    ) -> type[BaseModel]:
        """
        Converts JSON Schema object properties to a Pydantic model.
        :param name: The name of the model.
        :param schema: The properties of the JSON Schema object.
        :param required_keys: List of required keys in the schema.
        :return: A Pydantic model class.
        """
        fields = cls._parse_properties(schema, required_keys, **kwargs)
        return create_model(name, **fields)

    @classmethod
    def _parse_properties(
        cls,
        properties: dict[str, Any],
        required_keys: list[str],
        **kwargs: Unpack[TypeParserOptions],
    ) -> dict[str, tuple[type, Field]]:
        required_keys = required_keys or []

        fields = {}
        for name, prop in properties.items():
            sub_property = kwargs.copy()
            sub_property["required"] = name in required_keys

            parsed_type, parsed_properties = GenericTypeParser.type_from_properties(
                name, prop, **sub_property
            )
            fields[name] = (parsed_type, Field(**parsed_properties))

        return fields
