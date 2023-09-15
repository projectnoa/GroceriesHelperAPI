# Define schemas for validation

ingredient_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "name": {"type": "string"},
        "location_id": {"type": "number"}
    },
    "required": ["name", "location_id"]
}

location_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "name": {"type": "string"},
    },
    "required": ["name"]
}

dish_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "name": {"type": "string"},
        "ingredients": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "ingredient_id": {"type": "number"},
                    "quantity": {"type": "string"}
                },
                "required": ["ingredient_id", "quantity"]
            }
        }
    },
    "required": ["name", "ingredients"]
}

grocery_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "number"},
        "name": {"type": "string"},
        "ingredient_id": {"type": "number"}
    },
    "required": ["name", "ingredient_id"]
}

schemas = {
    "ingredients": ingredient_schema,
    "locations": location_schema,
    "dishes": dish_schema,
    "groceries": grocery_schema
}