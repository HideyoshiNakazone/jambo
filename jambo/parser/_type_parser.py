from jambo.types.type_parser_options import TypeParserOptions

from pydantic import Field, TypeAdapter
from typing_extensions import Annotated, Any, Generic, Self, TypeVar, Unpack

from abc import ABC, abstractmethod


T = TypeVar("T")


class GenericTypeParser(ABC, Generic[T]):
    json_schema_type: str = None

    type_mappings: dict[str, str] = {}

    default_mappings = {
        "default": "default",
        "description": "description",
    }

    @abstractmethod
    def from_properties_impl(
        self, name: str, properties: dict[str, Any], **kwargs: Unpack[TypeParserOptions]
    ) -> tuple[T, dict]:
        """
        Abstract method to convert properties to a type and its fields properties.
        :param name: The name of the type.
        :param properties: The properties of the type.
        :param kwargs: Additional options for type parsing.
        :return: A tuple containing the type and its properties.
        """

    def from_properties(
        self, name: str, properties: dict[str, Any], **kwargs: Unpack[TypeParserOptions]
    ) -> tuple[T, dict]:
        """
        Converts properties to a type and its fields properties.
        :param name: The name of the type.
        :param properties: The properties of the type.
        :param kwargs: Additional options for type parsing.
        :return: A tuple containing the type and its properties.
        """
        parsed_type, parsed_properties = self.from_properties_impl(
            name, properties, **kwargs
        )

        if not self._validate_default(parsed_type, parsed_properties):
            raise ValueError(
                f"Default value {properties.get('default')} is not valid for type {parsed_type.__name__}"
            )

        return parsed_type, parsed_properties

    @classmethod
    def type_from_properties(
        cls, name: str, properties: dict[str, Any], **kwargs: Unpack[TypeParserOptions]
    ) -> tuple[type, dict]:
        """
        Factory method to fetch the appropriate type parser based on properties
        and generates the equivalent type and fields.
        :param name: The name of the type to be created.
        :param properties: The properties that define the type.
        :param kwargs: Additional options for type parsing.
        :return: A tuple containing the type and its properties.
        """
        parser = cls._get_impl(properties)

        return parser().from_properties(name=name, properties=properties, **kwargs)

    @classmethod
    def _get_impl(cls, properties: dict[str, Any]) -> type[Self]:
        for subcls in cls.__subclasses__():
            schema_type, schema_value = subcls._get_schema_type()

            if schema_type not in properties:
                continue

            if schema_value is None or schema_value == properties[schema_type]:
                return subcls

        raise ValueError("Unknown type")

    @classmethod
    def _get_schema_type(cls) -> tuple[str, str | None]:
        if cls.json_schema_type is None:
            raise RuntimeError(
                f"TypeParser: json_schema_type not defined for subclass {cls.__name__}"
            )

        schema_definition = cls.json_schema_type.split(":")

        if len(schema_definition) == 1:
            return schema_definition[0], None

        return schema_definition[0], schema_definition[1]

    def mappings_properties_builder(
        self, properties, **kwargs: Unpack[TypeParserOptions]
    ) -> dict[str, Any]:
        if not kwargs.get("required", False):
            properties["default"] = properties.get("default", None)

        mappings = self.default_mappings | self.type_mappings

        return {
            mappings[key]: value for key, value in properties.items() if key in mappings
        }

    @staticmethod
    def _validate_default(field_type: type, field_prop: dict) -> bool:
        value = field_prop.get("default")

        if value is None and field_prop.get("default_factory") is not None:
            value = field_prop["default_factory"]()

        if value is None:
            return True

        try:
            field = Annotated[field_type, Field(**field_prop)]
            TypeAdapter(field).validate_python(value)
        except Exception as _:
            return False

        return True
