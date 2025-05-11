from jambo.parser import GenericTypeParser
from jambo.types.json_schema_type import JSONSchema

from jsonschema.exceptions import SchemaError
from jsonschema.validators import validator_for
from pydantic import create_model
from pydantic.fields import Field
from pydantic.main import ModelT


class SchemaConverter:
    """
    Converts JSON Schema to Pydantic models.

    This class is responsible for converting JSON Schema definitions
    into Pydantic models.  It validates the schema and generates
    the corresponding Pydantic model with appropriate fields and types.
    The generated model can be used for data validation and serialization.
    """

    @staticmethod
    def build(schema: JSONSchema) -> ModelT:
        """
        Converts a JSON Schema to a Pydantic model.
        :param schema: The JSON Schema to convert.
        :return: A Pydantic model class.
        """
        if "title" not in schema:
            raise ValueError("JSON Schema must have a title.")

        return SchemaConverter.build_object(schema["title"], schema)

    @staticmethod
    def build_object(
        name: str,
        schema: JSONSchema,
    ) -> ModelT:
        """
        Converts a JSON Schema object to a Pydantic model given a name.
        :param name:
        :param schema:
        :return:
        """

        try:
            validator = validator_for(schema)
            validator.check_schema(schema)
        except SchemaError as e:
            raise ValueError(f"Invalid JSON Schema: {e}") from e

        if schema["type"] != "object":
            raise TypeError(
                f"Invalid JSON Schema: {schema['type']}. Only 'object' can be converted to Pydantic models."  # noqa: E501
            )

        return SchemaConverter._build_model_from_properties(
            name, schema["properties"], schema.get("required", [])
        )

    @staticmethod
    def _build_model_from_properties(
        model_name: str, model_properties: dict, required_keys: list[str]
    ) -> ModelT:
        properties = SchemaConverter._parse_properties(model_properties, required_keys)

        return create_model(model_name, **properties)

    @staticmethod
    def _parse_properties(
        properties: dict, required_keys=None
    ) -> dict[str, tuple[type, Field]]:
        required_keys = required_keys or []

        fields = {}
        for name, prop in properties.items():
            is_required = name in required_keys
            fields[name] = SchemaConverter._build_field(name, prop, is_required)

        return fields

    @staticmethod
    def _build_field(name, properties: dict, required=False) -> tuple[type, Field]:
        match properties:
            case {"anyOf": _}:
                _field_type = "anyOf"
            case {"allOf": _}:
                _field_type = "allOf"
            case {"type": _}:
                _field_type = properties["type"]
            case _:
                raise ValueError(f"Invalid JSON Schema: {properties}")

        _field_type, _field_args = GenericTypeParser.get_impl(
            _field_type
        ).from_properties(name, properties, required)

        return _field_type, Field(**_field_args)
