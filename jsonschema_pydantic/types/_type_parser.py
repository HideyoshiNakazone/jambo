from abc import ABC, abstractmethod
from typing import Generic, Self, TypeVar

T = TypeVar("T")


class GenericTypeParser(ABC, Generic[T]):
    @property
    @abstractmethod
    def mapped_type(self) -> type[T]: ...

    @property
    @abstractmethod
    def json_schema_type(self) -> str: ...

    @staticmethod
    @abstractmethod
    def from_properties(
        name: str, properties: dict[str, any]
    ) -> tuple[type[T], dict[str, any]]: ...

    @classmethod
    def get_impl(cls, type_name: str) -> Self:
        for subcls in cls.__subclasses__():
            if subcls.json_schema_type == type_name:
                return subcls

        raise ValueError(f"Unknown type: {type_name}")
