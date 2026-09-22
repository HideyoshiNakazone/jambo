# Jambo - JSON Schema to Pydantic Converter

<p style="text-align:center">
<a href="https://github.com/HideyoshiNakazone/jambo" target="_blank">
 <img src="https://img.shields.io/github/last-commit/HideyoshiNakazone/jambo.svg" alt="Last commit">
 <img src="https://github.com/HideyoshiNakazone/jambo/actions/workflows/build.yml/badge.svg" alt="Tests">
</a>
<a href="https://codecov.io/gh/HideyoshiNakazone/jambo" target="_blank">
    <img src="https://codecov.io/gh/HideyoshiNakazone/jambo/branch/main/graph/badge.svg" alt="Coverage">
</a>
<br />
<a href="https://pypi.org/project/jambo" target="_blank">
    <img src="https://badge.fury.io/py/jambo.svg" alt="Package version">
    <img src="https://static.pepy.tech/personalized-badge/jambo?period=total&units=INTERNATIONAL_SYSTEM&left_color=GREY&right_color=GREEN&left_text=downloads" alt="PyPI Downloads">
</a>
<a href="https://github.com/HideyoshiNakazone/jambo" target="_blank">
    <img src="https://img.shields.io/pypi/pyversions/jambo.svg" alt="Python versions">
    <img src="https://img.shields.io/github/license/HideyoshiNakazone/jambo.svg" alt="License">
</a>
</p>

**Jambo** is a Python package that automatically converts [JSON Schema](https://json-schema.org/) definitions into [Pydantic](https://docs.pydantic.dev/) models. 
It's designed to streamline schema validation and enforce type safety using Pydantic's validation features.

Created to simplify the process of dynamically generating Pydantic models for AI frameworks like [LangChain](https://www.langchain.com/), [CrewAI](https://www.crewai.com/), and others.

---


## ✨ Features

- ✅ Convert JSON Schema into Pydantic models dynamically;
- 🔒 Supports validation for:
    - strings
    - integers
    - floats
    - booleans
    - arrays
    - nested objects
    - allOf
    - anyOf
    - oneOf
    - ref
    - enum
    - const
- ⚙️ Enforces constraints like `minLength`, `maxLength`, `pattern`, `minimum`, `maximum`, `uniqueItems`, and more;
- 📦 Zero config — just pass your schema and get a model.

---

## 📦 Installation

```bash
pip install jambo
```

---

## 🚀 Usage

There are two ways to build models with Jambo:

1. The original static API: `SchemaConverter.build(schema)` doesn't persist any reference cache between calls and doesn't require any configuration.
2. The new instance API: use a `SchemaConverter()` instance and call `build_with_cache`, which exposes and persists a reference cache and helper methods.

The instance API is useful when you want to reuse generated subtypes, inspect cached models, or share caches between converters; all leveraging namespaces via the `$id` property in JSON Schema. See the docs for full details: https://jambo.readthedocs.io/en/latest/usage.ref_cache.html


### Static (compatibility) example

```python
from jambo import SchemaConverter

schema = {
    "title": "Person",
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
    },
    "required": ["name"],
}

# Old-style convenience API (kept for compatibility)
Person = SchemaConverter.build(schema)

obj = Person(name="Alice", age=30)
print(obj)
```

### Instance API (recommended for cache control)

```python
from jambo import SchemaConverter

converter = SchemaConverter()

schema = {
    "title": "Person",
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"},
        "address": {"type": "object", "properties": {"street": {"type": "string"}}},
    },
    "required": ["name"],
}

# build_with_cache populates the converter's instance-level ref cache
Person = converter.build_with_cache(schema)

# you can retrieve cached subtypes by name/path
cached_person = converter.get_cached_ref("Person")
# clear the instance cache when needed
converter.clear_ref_cache()
```

---

## ✅ Example Validations

Following are some examples of how to use Jambo to create Pydantic models with various JSON Schema features, but for more information, please refer to the [documentation](https://jambo.readthedocs.io/).

### Strings with constraints

```python
from jambo import SchemaConverter


schema = {
    "title": "EmailExample",
    "type": "object",
    "properties": {
        "email": {
            "type": "string",
            "minLength": 5,
            "maxLength": 50,
            "pattern": r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        },
    },
    "required": ["email"],
}

Model = SchemaConverter.build(schema)
obj = Model(email="user@example.com")
print(obj)
```

### Integers with bounds

```python
from jambo import SchemaConverter


schema = {
    "title": "AgeExample",
    "type": "object",
    "properties": {
        "age": {"type": "integer", "minimum": 0, "maximum": 120}
    },
    "required": ["age"],
}

Model = SchemaConverter.build(schema)
obj = Model(age=25)
print(obj)
```

### Nested Objects

```python
from jambo import SchemaConverter


schema = {
    "title": "NestedObjectExample",
    "type": "object",
    "properties": {
        "address": {
            "type": "object",
            "properties": {
                "street": {"type": "string"},
                "city": {"type": "string"},
            },
            "required": ["street", "city"],
        }
    },
    "required": ["address"],
}

Model = SchemaConverter.build(schema)
obj = Model(address={"street": "Main St", "city": "Gotham"})
print(obj)
```

### References

```python
from jambo import SchemaConverter


schema = {
    "title": "person",
    "$ref": "#/$defs/person",
    "$defs": {
        "person": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "emergency_contact": {
                    "$ref": "#/$defs/person",
                },
            },
        }
    },
}

model = SchemaConverter.build(schema)

obj = model(
    name="John",
    age=30,
    emergency_contact=model(
        name="Jane",
        age=28,
    ),
)
```

---

## 🧪 Running Tests

To run the test suite:

```bash
poe tests
```

Or manually:

```bash
python -m unittest discover -s tests -v
```

---

## 🛠 Development Setup

To set up the project locally:

1. Clone the repository
2. Install [uv](https://github.com/astral-sh/uv) (if not already installed)
3. Install dependencies:

```bash
uv sync
```

4. Set up git hooks:

```bash
poe create-hooks
```

---

## 📌 Roadmap / TODO

- [ ] Better error reporting for unsupported schema types

---

## 🤝 Contributing

PRs are welcome! This project uses MIT for licensing, so feel free to fork and modify as you see fit.

---

## 🧾 License

MIT License.
