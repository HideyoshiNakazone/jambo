from jambo.parser._type_parser import GenericTypeParser

from pydantic import EmailStr, HttpUrl, IPvAnyAddress

from datetime import date, datetime, time


class StringTypeParser(GenericTypeParser):
    mapped_type = str

    json_schema_type = "string"

    type_mappings = {
        "maxLength": "max_length",
        "minLength": "min_length",
        "pattern": "pattern",
        "format": "format",
    }

    format_type_mapping = {
        "email": EmailStr,
        "uri": HttpUrl,
        "ipv4": IPvAnyAddress,
        "ipv6": IPvAnyAddress,
        "hostname": str,
        "date": date,
        "time": time,
        "date-time": datetime,
    }

    format_pattern_mapping = {
        "hostname": r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$",
    }

    def from_properties(self, name, properties, required=False):
        mapped_properties = self.mappings_properties_builder(properties, required)

        format_type = properties.get("format")
        if format_type:
            if format_type in self.format_type_mapping:
                mapped_type = self.format_type_mapping[format_type]
                if format_type in self.format_pattern_mapping:
                    mapped_properties["pattern"] = self.format_pattern_mapping[
                        format_type
                    ]
            else:
                raise ValueError(f"Unsupported string format: {format_type}")
        else:
            mapped_type = str

        default_value = properties.get("default")
        if default_value is not None:
            self.validate_default(mapped_type, mapped_properties, default_value)

        return mapped_type, mapped_properties
