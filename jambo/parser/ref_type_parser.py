from jambo.parser._type_parser import GenericTypeParser

from typing import ForwardRef, Union


class RefTypeParser(GenericTypeParser):
    mapped_type = any

    json_schema_type = "$ref"

    type_mappings = {}

    def from_properties(
        self, properties, name, context, required=False, **kwargs
    ) -> tuple[Union[type, ForwardRef], dict]:
        if "$ref" not in properties:
            raise ValueError(f"RefTypeParser: Missing $ref in properties for {name}")

        if context is None:
            raise RuntimeError(
                f"RefTypeParser: Missing $content in properties for {name}"
            )

        if not properties["$ref"].startswith("#"):
            raise ValueError(
                "At the moment, only local references are supported. Look into $defs and # for recursive references."
            )

        ref_type = None
        mapped_properties = dict()

        if properties["$ref"] == "#":
            if "title" not in context:
                raise ValueError(
                    "RefTypeParser: Missing title in properties for $ref #"
                )

            ref_type = ForwardRef(context["title"])

        elif properties["$ref"].startswith("#/$defs/"):
            target_property = context
            for prop_name in properties["$ref"].split("/")[1:]:
                if prop_name not in target_property:
                    raise ValueError(
                        f"RefTypeParser: Missing {prop_name} in properties for $ref {properties['$ref']}"
                    )
                target_property = target_property[prop_name]

            ref_type, mapped_properties = GenericTypeParser.type_from_properties(
                prop_name, target_property, context=context, **kwargs
            )

        else:
            raise ValueError(
                "RefTypeParser: Invalid $ref format. Only local references are supported."
            )

        if not required:
            mapped_properties["default"] = None

        return ref_type, mapped_properties
