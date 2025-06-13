from jambo.parser import GenericTypeParser
from jambo.types.type_parser_options import TypeParserOptions

from typing_extensions import Any, ForwardRef, Literal, TypeVar, Union, Unpack


RefType = TypeVar("RefType", bound=Union[type, ForwardRef])


class RefTypeParser(GenericTypeParser):
    json_schema_type = "$ref"

    def from_properties_impl(
        self, name: str, properties: dict[str, Any], **kwargs: Unpack[TypeParserOptions]
    ) -> tuple[RefType, dict]:
        if "$ref" not in properties:
            raise ValueError(f"RefTypeParser: Missing $ref in properties for {name}")

        context = kwargs["context"]
        ref_cache = kwargs["ref_cache"]

        mapped_type = None
        mapped_properties = self.mappings_properties_builder(properties, **kwargs)

        if context is None:
            raise RuntimeError(
                f"RefTypeParser: Missing $content in properties for {name}"
            )

        if not properties["$ref"].startswith("#"):
            raise ValueError(
                "At the moment, only local references are supported. "
                "Look into $defs and # for recursive references."
            )

        ref_strategy, ref_name, ref_property = self._examine_ref_strategy(
            name, properties, **kwargs
        )

        # In this code ellipsis is used to indicate that the reference is still being processed,
        # If the reference is already in the cache, return it.
        ref_state = ref_cache.setdefault(ref_name)

        if ref_state is Ellipsis:
            return ForwardRef(ref_name), mapped_properties
        elif ref_state is not None:
            return ref_state, mapped_properties
        else:
            ref_cache[ref_name] = Ellipsis

        match ref_strategy:
            case "forward_ref":
                mapped_type = ForwardRef(ref_name)
            case "def_ref":
                mapped_type, _ = GenericTypeParser.type_from_properties(
                    ref_name, ref_property, **kwargs
                )
            case _:
                raise ValueError(
                    f"RefTypeParser: Unsupported $ref {properties['$ref']}"
                )

        # Sets cached reference to the mapped type
        ref_cache[ref_name] = mapped_type

        return mapped_type, mapped_properties

    def _examine_ref_strategy(
        self, name: str, properties: dict[str, Any], **kwargs: Unpack[TypeParserOptions]
    ) -> tuple[Literal["forward_ref", "def_ref"], str, dict]:
        if properties["$ref"] == "#":
            ref_name = kwargs["context"].get("title")
            if ref_name is None:
                raise ValueError(
                    f"RefTypeParser: Missing title in properties for $ref {properties['$ref']}"
                )
            return "forward_ref", ref_name, {}

        if properties["$ref"].startswith("#/$defs/"):
            target_name, target_property = self._extract_target_ref(
                name, properties, **kwargs
            )
            return "def_ref", target_name, target_property

        raise ValueError(f"RefTypeParser: Unsupported $ref {properties['$ref']}")

    def _extract_target_ref(
        self, name: str, properties: dict[str, Any], **kwargs: Unpack[TypeParserOptions]
    ) -> tuple[str, dict]:
        target_name = None
        target_property = kwargs["context"]
        for prop_name in properties["$ref"].split("/")[1:]:
            if prop_name not in target_property:
                raise ValueError(
                    f"RefTypeParser: Missing {prop_name} in"
                    " properties for $ref {properties['$ref']}"
                )
            target_name = prop_name
            target_property = target_property[prop_name]

        if target_name is None or target_property is None:
            raise ValueError(f"RefTypeParser: Invalid $ref {properties['$ref']}")

        return target_name, target_property
