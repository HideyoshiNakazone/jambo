from jambo.parser import ObjectTypeParser, RefTypeParser
from jambo.types.json_schema_type import JSONSchema

from jsonschema.exceptions import SchemaError
from jsonschema.validators import validator_for
from pydantic import BaseModel


class SchemaConverter:
    """
    Converts JSON Schema to Pydantic models.

    This class is responsible for converting JSON Schema definitions into Pydantic models.
    It validates the schema and generates the corresponding Pydantic model with appropriate
    fields and types. The generated model can be used for data validation and serialization.
    """

    @staticmethod
    def build(schema: JSONSchema) -> type[BaseModel]:
        """
        Converts a JSON Schema to a Pydantic model.
        :param schema: The JSON Schema to convert.
        :return: A Pydantic model class.
        """

        try:
            validator = validator_for(schema)
            validator.check_schema(schema)
        except SchemaError as e:
            raise ValueError(f"Invalid JSON Schema: {e}")

        if "title" not in schema:
            raise ValueError("JSON Schema must have a title.")

        schema_type = SchemaConverter._get_schema_type(schema)

        parsed_model = None
        match schema_type:
            case "object":
                parsed_model = SchemaConverter._from_object(schema)
            case "$ref":
                parsed_model, _ = RefTypeParser().from_properties(
                    schema["title"],
                    schema,
                    context=schema,
                    ref_cache=dict(),
                    required=True,
                )
            case _:
                raise TypeError(f"Unsupported schema type: {schema_type}")

        if not issubclass(parsed_model, BaseModel):
            raise TypeError(
                f"Parsed model {parsed_model.__name__} is not a subclass of BaseModel."
            )

        return parsed_model

    @staticmethod
    def _from_object(schema: JSONSchema) -> type[BaseModel]:
        """
        Converts a JSON Schema object to a Pydantic model.
        :param schema: The JSON Schema object to convert.
        :return: A Pydantic model class.
        """

        if "properties" not in schema:
            raise ValueError("JSON Schema object must have properties defined.")

        return ObjectTypeParser.to_model(
            schema["title"],
            schema["properties"],
            schema.get("required", []),
            context=schema,
            ref_cache=dict(),
        )

    @staticmethod
    def _get_schema_type(schema: JSONSchema) -> str:
        """
        Returns the type of the schema.
        :param schema: The JSON Schema to check.
        :return: The type of the schema.
        """
        if "$ref" in schema:
            return "$ref"

        return schema.get("type", "undefined")
