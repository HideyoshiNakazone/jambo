from jambo.exceptions import InternalAssertionException, InvalidSchemaException
from jambo.parser._type_parser import GenericTypeParser
from jambo.types.json_schema_type import JSONSchema
from jambo.types.type_parser_options import TypeParserOptions

from pydantic import BaseModel, ConfigDict, Field, create_model
from pydantic.fields import FieldInfo
from typing_extensions import Unpack

import re
import warnings


class ObjectTypeParser(GenericTypeParser):
    mapped_type = object

    json_schema_type = "type:object"

    _valid_name_pattern = re.compile(r"^[a-zA-Z0-9_-]+(?:\.[a-zA-Z0-9_-]+)*$")

    def from_properties_impl(
        self, name: str, properties: JSONSchema, **kwargs: Unpack[TypeParserOptions]
    ) -> tuple[type[BaseModel], dict]:
        type_parsing = self.to_model(
            name,
            properties.get("properties", {}),
            properties.get("required", []),
            description=properties.get("description"),
            **kwargs,
        )
        type_properties = self.mappings_properties_builder(properties, **kwargs)

        if (
            default_value := type_properties.pop("default", None)
        ) is not None or not kwargs.get("required", False):
            type_properties["default_factory"] = (
                lambda: type_parsing.model_validate(default_value)
                if default_value is not None
                else None
            )

        if (example_values := type_properties.pop("examples", None)) is not None:
            type_properties["examples"] = [
                type_parsing.model_validate(example) for example in example_values
            ]

        return type_parsing, type_properties

    @classmethod
    def to_model(
        cls,
        name: str,
        properties: dict[str, JSONSchema],
        required_keys: list[str],
        description: str | None = None,
        **kwargs: Unpack[TypeParserOptions],
    ) -> type[BaseModel]:
        """
        Converts JSON Schema object properties to a Pydantic model.
        :param name: The name of the model.
        :param properties: The properties of the JSON Schema object.
        :param required_keys: List of required keys in the schema.
        :return: A Pydantic model class.
        """
        if not cls._valid_name_pattern.match(name):
            raise InvalidSchemaException(
                f"Invalid name '{name}' for the schema. Object titles and property names"
                " must use alphanumeric characters, hyphens and underscores only."
            )

        ref_cache = kwargs.get("ref_cache")
        if ref_cache is None:
            raise InternalAssertionException(
                "`ref_cache` must be provided in kwargs for ObjectTypeParser"
            )

        if (model := ref_cache.get(name)) is not None and isinstance(model, type):
            warnings.warn(
                f"Type '{name}' is already in the ref_cache and therefore cached value will be used."
                " This may indicate a namming collision in the schema or just a normal optimization,"
                " if this behavior is desired pass a clean ref_cache or use the param `without_cache`"
            )
            return model

        model_config = ConfigDict(validate_assignment=True)
        fields = cls._parse_properties(name, properties, required_keys, **kwargs)

        model = create_model(
            name, __config__=model_config, __doc__=description, **fields
        )  # type: ignore
        ref_cache[name] = model

        return model

    @classmethod
    def _parse_properties(
        cls,
        name: str,
        properties: dict[str, JSONSchema],
        required_keys: list[str],
        **kwargs: Unpack[TypeParserOptions],
    ) -> dict[str, tuple[type, FieldInfo]]:
        required_keys = required_keys or []

        fields = {}
        for field_name, field_prop in properties.items():
            sub_property: TypeParserOptions = kwargs.copy()
            sub_property["required"] = field_name in required_keys

            parsed_type, parsed_properties = GenericTypeParser.type_from_properties(
                f"{name}.{field_name}",
                field_prop,
                **sub_property,  # type: ignore
            )
            fields[field_name] = (parsed_type, Field(**parsed_properties))

        return fields
