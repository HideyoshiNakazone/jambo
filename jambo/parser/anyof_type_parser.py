from jambo.parser._type_parser import GenericTypeParser
from jambo.types.type_parser_options import TypeParserOptions

from pydantic import Field
from typing_extensions import Annotated, Union, Unpack


class AnyOfTypeParser(GenericTypeParser):
    mapped_type = Union

    json_schema_type = "anyOf"

    def from_properties_impl(
        self, name, properties, **kwargs: Unpack[TypeParserOptions]
    ):
        if "anyOf" not in properties:
            raise ValueError(f"Invalid JSON Schema: {properties}")

        if not isinstance(properties["anyOf"], list):
            raise ValueError(f"Invalid JSON Schema: {properties['anyOf']}")

        mapped_properties = self.mappings_properties_builder(properties, **kwargs)

        sub_properties = properties["anyOf"]

        sub_types = [
            GenericTypeParser.type_from_properties(name, subProperty, **kwargs)
            for subProperty in sub_properties
        ]

        if not kwargs.get("required", False):
            mapped_properties["default"] = mapped_properties.get("default")

        # By defining the type as Union of Annotated type we can use the Field validator
        # to enforce the constraints of each union type when needed.
        # We use Annotated to attach the Field validators to the type.
        # Only wrap in Annotated[T, Field(**v)] if there are meaningful field constraints
        # Don't wrap for simple cases where v only contains {'default': None}
        field_types = [
            Annotated[t, Field(**v)] if self._has_meaningful_constraints(v) else t
            for t, v in sub_types
        ]

        return Union[(*field_types,)], mapped_properties

    @staticmethod
    def _has_meaningful_constraints(field_props):
        """
        Check if field properties contain meaningful constraints that require Field wrapping.

        Returns False if:
        - field_props is None or empty
        - field_props only contains {'default': None}

        Returns True if:
        - field_props contains a non-None default value
        - field_props contains other constraint properties (min_length, max_length, pattern, etc.)
        """
        if not field_props:
            return False

        # If only default is set and it's None, no meaningful constraints
        if len(field_props) == 1 and field_props.get('default') is None:
            return False

        # If there are multiple properties or non-None default, that's meaningful
        return True