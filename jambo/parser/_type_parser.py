from jambo.types.json_schema_type import JSONSchema

from pydantic import Field, TypeAdapter
from typing_extensions import Annotated, Self, Unpack

from abc import ABC, abstractmethod
from typing import Generic, NotRequired, Optional, TypedDict, TypeVar


T = TypeVar("T")


class TypeParserOptions(TypedDict):
    """
    Options for type parsers.
    """

    required: bool
    context: NotRequired[JSONSchema]


class GenericTypeParser(ABC, Generic[T]):
    json_schema_type: str = None

    default_mappings = {
        "default": "default",
        "description": "description",
    }

    type_mappings: dict[str, str] = None

    @classmethod
    def type_from_properties(
        cls,
        name: str,
        properties: dict[str, any],
        /,
        **kwargs: Unpack[TypeParserOptions],
    ) -> tuple[T, dict]:
        parser = cls._get_impl(properties)

        return parser.from_properties(name, properties, **kwargs)

    @classmethod
    def _get_impl(cls, properties: dict) -> Self:
        for subcls in cls.__subclasses__():
            schema_type, schema_value = subcls._get_schema_type()

            if schema_type not in properties:
                continue

            if schema_value is None or schema_value == properties[schema_type]:
                return subcls()

        raise ValueError("Unknown type")

    @classmethod
    def _get_schema_type(cls) -> tuple[str, Optional[str]]:
        if cls.json_schema_type is None:
            raise RuntimeError("TypeParser: json_schema_type not defined")

        schema_definition = cls.json_schema_type.split(":")

        if len(schema_definition) == 1:
            return schema_definition[0], None

        return schema_definition[0], schema_definition[1]

    @abstractmethod
    def from_properties(
        self,
        name: str,
        properties: dict[str, any],
        /,
        **kwargs: Unpack[TypeParserOptions],
    ) -> tuple[T, dict]: ...

    def mappings_properties_builder(self, properties, required=False) -> dict[str, any]:
        if self.type_mappings is None:
            raise NotImplementedError("Type mappings not defined")

        if not required:
            properties["default"] = properties.get("default", None)

        mappings = self.default_mappings | self.type_mappings

        return {
            mappings[key]: value for key, value in properties.items() if key in mappings
        }

    def validate_default(self, field_type: type, field_prop: dict, value) -> None:
        field = Annotated[field_type, Field(**field_prop)]
        TypeAdapter(field).validate_python(value)
