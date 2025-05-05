from jambo.parser._type_parser import GenericTypeParser


class AllOfTypeParser(GenericTypeParser):
    mapped_type = any

    json_schema_type = "allOf"

    def from_properties(self, name, properties, required=False, **kwargs):
        subProperties = properties.get("allOf")
        if not subProperties:
            raise ValueError("Invalid JSON Schema: 'allOf' is not specified.")

        _mapped_type = properties.get("type")
        if _mapped_type is None:
            _mapped_type = subProperties[0].get("type")

        if _mapped_type is None:
            raise ValueError("Invalid JSON Schema: 'type' is not specified.")

        if any(
            prop.get("type", _mapped_type) != _mapped_type for prop in subProperties
        ):
            raise ValueError("Invalid JSON Schema: allOf types do not match.")

        for subProperty in subProperties:
            # If a sub-property has not defined a type,
            # we need to set it to the top-level type
            subProperty["type"] = _mapped_type

        combined_properties = self._rebuild_properties_from_subproperties(subProperties)

        return GenericTypeParser.type_from_properties(
            name, combined_properties, required=required, **kwargs
        )

    def _rebuild_properties_from_subproperties(self, subProperties):
        properties = {}
        for subProperty in subProperties:
            for name, prop in subProperty.items():
                if name not in properties:
                    properties[name] = prop
                else:
                    # Merge properties if they exist in both sub-properties
                    properties[name] = AllOfTypeParser._validate_prop(
                        name, properties[name], prop
                    )
        return properties

    @staticmethod
    def _validate_prop(prop_name, old_value, new_value):
        if prop_name == "description":
            return f"{old_value} | {new_value}"

        if prop_name == "default":
            if old_value != new_value:
                raise ValueError(
                    f"Invalid JSON Schema: conflicting defaults for '{prop_name}'"
                )
            return old_value

        if prop_name == "required":
            return old_value + new_value

        if prop_name in ("maxLength", "maximum", "exclusiveMaximum"):
            return old_value if old_value > new_value else new_value

        if prop_name in ("minLength", "minimum", "exclusiveMinimum"):
            return old_value if old_value < new_value else new_value

        if prop_name == "properties":
            for key, value in new_value.items():
                if key not in old_value:
                    old_value[key] = value
                    continue

                for sub_key, sub_value in value.items():
                    if sub_key not in old_value[key]:
                        old_value[key][sub_key] = sub_value
                    else:
                        # Merge properties if they exist in both sub-properties
                        old_value[key][sub_key] = AllOfTypeParser._validate_prop(
                            sub_key, old_value[key][sub_key], sub_value
                        )

        # Handle other properties by just returning the first valued
        return old_value
