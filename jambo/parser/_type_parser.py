from pydantic import Field, TypeAdapter
from typing_extensions import Self

from abc import ABC, abstractmethod
from typing import Annotated, Generic, TypeVar


T = TypeVar("T")


class GenericTypeParser(ABC, Generic[T]):
    mapped_type: type[T] = None

    json_schema_type: str = None

    default_mappings = {
        "default": "default",
        "description": "description",
    }

    type_mappings: dict[str, str] = None

    @classmethod
    def get_impl(cls, type_name: str) -> Self:
        for subcls in cls.__subclasses__():
            if subcls.json_schema_type is None:
                raise RuntimeError(f"Unknown type: {type_name}")

            if subcls.json_schema_type == type_name:
                return subcls()

        raise ValueError(f"Unknown type: {type_name}")

    @abstractmethod
    def from_properties(
        self, name: str, properties: dict[str, any], required: bool = False
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
