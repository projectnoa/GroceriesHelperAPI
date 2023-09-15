# Validation function
from jsonschema import validate, ValidationError

def validate_data_against_schema(data, schema):
    """Validate data against the provided schema."""
    try:
        validate(instance=data, schema=schema)
        return True, None
    except ValidationError as e:
        return False, str(e)
