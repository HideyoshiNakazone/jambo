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

    This class is responsible for converting JSON Schema definitions into Pydantic
    models. It validates the schema and generates the corresponding Pydantic model
    with appropriate fields and types. The generated model can be used for data
    validation and serialization.
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
        **kwargs,
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

        if "type" not in schema or schema["type"] != "object":
            raise TypeError(
                f"Invalid JSON Schema: {schema.get('type', 'Unknown')}. "
                "Only 'object' can be converted to Pydantic models."
            )

        properties = SchemaConverter._parse_properties(
            schema.get("properties"), required_keys=schema.get("required", []), **kwargs
        )

        return create_model(name, **properties)

    @staticmethod
    def _parse_properties(
        properties: dict, context=None, required_keys=None, **kwargs
    ) -> dict[str, tuple[type, Field]]:
        if context is None:
            context = properties
        required_keys = required_keys or []

        fields = {}
        for name, prop in properties.items():
            is_field_required = name in required_keys

            field_type, field_validators = GenericTypeParser.type_from_properties(
                name,
                prop,
                context=context,
                required=is_field_required,
            )
            fields[name] = (field_type, Field(**field_validators))

        return fields
