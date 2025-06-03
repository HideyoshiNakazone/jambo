from jambo.parser._type_parser import GenericTypeParser
from jambo.types.type_parser_options import TypeParserOptions

from typing_extensions import TypeVar, Unpack

import copy


V = TypeVar("V")


class ArrayTypeParser(GenericTypeParser):
    mapped_type = list

    json_schema_type = "type:array"

    default_mappings = {"description": "description"}

    type_mappings = {
        "maxItems": "max_length",
        "minItems": "min_length",
    }

    def from_properties(self, name, properties, **kwargs: Unpack[TypeParserOptions]):
        item_properties = kwargs.copy()
        item_properties["required"] = True
        _item_type, _item_args = GenericTypeParser.type_from_properties(
            name, properties["items"], **item_properties
        )

        wrapper_type = set if properties.get("uniqueItems", False) else list
        field_type = wrapper_type[_item_type]

        mapped_properties = self.mappings_properties_builder(properties, **kwargs)

        default_list = properties.pop("default", None)
        if default_list is not None:
            self.validate_default(
                field_type,
                mapped_properties,
                default_list,
            )

            if wrapper_type is list:
                mapped_properties["default_factory"] = lambda: copy.deepcopy(
                    wrapper_type(default_list)
                )
            else:
                mapped_properties["default_factory"] = lambda: wrapper_type(
                    default_list
                )

        return field_type, mapped_properties
