import json

from utils.validations import validate_data_against_schema
from data.schemas import schemas

# import boto3

# Initialize client
# s3 = boto3.client('s3')
# Initialize keys
bucket = 'groceries-helper'
json_file_name = 'groceries-helper-db.json'

class DataException(Exception):
    pass

class DataNotFoundException(DataException):
    pass

class DataEmptyException(DataException):
    pass

class S3NotAvailableException(DataException):
    pass

class InvalidDataOperationException(DataException):
    pass

def add_data_to(data, new, resource):
    """
    Method to add data to the database json object residing in S3.

    Parameters
    ----------
    data: dict
        The full json object.
    new: dict
        The new entity to add.
    resource: str
        The name of the entity to add.
    ----------

    Returns
    ----------
    dict
        The updated json object.
    ----------
    """

    if new == None or new == {}:
        raise DataEmptyException("No entity provided.")
    if data == None or data == {}:
        raise DataEmptyException("No data provided.")
    if resource == None or resource == "":
        raise InvalidDataOperationException("No resource provided.")
    if resource not in data["data"]:
        raise InvalidDataOperationException("Invalid resource.")
    
    is_valid, error_message = validate_data_against_schema(new, schemas[resource])

    if not is_valid:
        raise InvalidDataOperationException(error_message)

    latest = data["data"][resource][-1]
    
    new["id"] = latest["id"] + 1
    
    data["data"][resource].append(new)
    
    return __update_data(data)
    
def edit_data_for(data, edited, resource):
    """
    Method to edit data in the database json object residing in S3.
    
    Parameters
    ----------
    data: dict
        The full json object.
    edited: dict
        The edited entity to update.
    resource: str
        The name of the entity to update.
    ----------

    Returns
    ----------
    dict
        The updated json object.
    ----------
    """

    if edited == None or edited == {}:
        raise DataEmptyException("No entity provided.")
    if data == None or data == {}:
        raise DataEmptyException("No data provided.")
    if resource == None or resource == "":
        raise InvalidDataOperationException("No resource provided.")
    if resource not in data["data"]:
        raise InvalidDataOperationException("Invalid resource.")
    
    is_valid, error_message = validate_data_against_schema(edited, schemas[resource])
    
    if not is_valid:
        raise InvalidDataOperationException(error_message)

    for idx, item in enumerate(data["data"][resource]):
        if item["id"] == edited["id"]:
            data["data"][resource][idx] = edited
            break

    return __update_data(data)
    
def delete_data_for(data, id, resource):
    """
    Method to delete data from the database json object residing in S3.

    Parameters
    ----------
    data: dict
        The full json object.
    id: int
        The ID of the entity to delete.
    resource: str
        The name of the entity to delete.
    ----------

    Returns
    ----------
    dict
        The updated json object.
    ----------
    """

    if id == None or id == "":
        raise InvalidDataOperationException("No ID provided.")
    if data == None or data == {}:
        raise DataEmptyException("No data provided.")
    if resource == None or resource == "":
        raise InvalidDataOperationException("No resource provided.")
    if resource not in data["data"]:
        raise InvalidDataOperationException("Invalid resource.")

    data["data"][resource] = [item for item in data["data"][resource] if item["id"] != id]
    # After deletion, validate and remove any dangling references
    __validate_and_remove_dangling_references_general(data["data"], id, resource)
    
    return __update_data(data)["data"][resource]

def get_data():
    """
    Method to get the data from the database json object residing in S3.

    Returns
    ----------
    dict
        The json object content.
    ----------
    """

    # Get data from S3 ###############################
    # # Check if S3 is available
    # if s3 == None:
    #     raise S3NotAvailableException("S3 is not available.")
    # # Get data
    # file_obj = s3.get_object(Bucket=bucket, Key=json_file_name)
    # # Check if the object and its body exist
    # if file_obj == None or file_obj["Body"] == None:
    #     raise DataNotFoundException("Data object not found.")
    # # Read file content
    # file_content = file_obj["Body"].read().decode('utf-8')
    ##################################################
    
    # Get data from file #############################
    with open(json_file_name, "r") as f:
        file_content = f.read()
    ##################################################

    if file_content == None:
        raise DataEmptyException("No data found.")

    # Parse data
    return json.loads(file_content)

def __update_data(data):
    """
    Method to update the data in the database json object residing in S3.

    Parameters
    ----------
    data: dict
        The full updated json object.
    ----------

    Returns
    ----------
    dict
        The updated json object.
    ----------
    """

    if data == None or data == {}:
        raise DataEmptyException("No data provided.")

    # Update data on S3 ##############################
    # # Check if S3 is available
    # if s3 == None:
    #     raise S3NotAvailableException("S3 is not available.")
    # # Update data
    # s3.put_object(Key=json_file_name, Bucket=bucket, Body=(bytes(json.dumps(data).encode('UTF-8'))))
    ##################################################
    
    # Update data in file ############################
    # # Update data
    with open(json_file_name, "w") as f:
        json.dump(data, f)
    ##################################################
    
    return data

def retrieve_referenced_entities(obj, data):
    """
    Method to recursively replace referenced entity IDs with their details.

    Parameters
    ----------
    obj: dict
        The entity to resolve.
    data: dict
        The full data dictionary.
    ----------

    Returns
    ----------
    dict
        The resolved entity.
    ----------
    """

    if obj == None or obj == {}:
        raise DataNotFoundException("Data object not found.")
    if data == None or data == {}:
        raise DataEmptyException("No data provided.")

    # If obj is a dictionary, iterate over its fields
    if isinstance(obj, dict):
        for field, value in list(obj.items()):  # Use list to prevent runtime error due to dictionary size change during iteration
            # Check if the field ends with "_id" (single reference) or "_ids" (multiple references)
            if field.endswith("_id"):
                entity_name = field[:-3] + "s"  # Convert singular to plural (e.g., ingredient_id -> ingredients)
                
                # Check if the entity_name exists in the data
                if entity_name in data:
                    referenced_entity = next((item for item in data[entity_name] if item["id"] == value), None)
                    if referenced_entity:
                        referenced_entity_data = retrieve_referenced_entities(referenced_entity.copy(), data)
                        obj.update(referenced_entity_data)
                        del obj[field]
            elif field.endswith("_ids"):
                entity_name = field[:-4] + "s"
                
                # Check if the entity_name exists in the data
                if entity_name in data:
                    referenced_entities = [item for item in data[entity_name] if item["id"] in value]
                    if referenced_entities:
                        referenced_entities_data = [retrieve_referenced_entities(item.copy(), data) for item in referenced_entities]
                        obj.update(referenced_entities_data)
                        del obj[field]
            else:
                # For other fields, continue resolving nested references recursively
                obj[field] = retrieve_referenced_entities(value, data)
    # If obj is a list, iterate over its items
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            obj[idx] = retrieve_referenced_entities(item, data)
    return obj

def __validate_and_remove_dangling_references_recursive(item, singular_ref, plural_ref, deleted_id):
    """
    Method to recursively remove references from a nested structure.

    Parameters
    ----------
    item: dict
        The nested structure to check.
    singular_ref: str
        The name of the singular reference field.
    plural_ref: str
        The name of the plural reference field.
    deleted_id: int
        The ID of the deleted item.
    ----------
    """

    if item == None or item == {}:
        raise DataNotFoundException("Data object not found.")
    if singular_ref == None or singular_ref == "":
        raise InvalidDataOperationException("Invalid singular reference.")
    if plural_ref == None or plural_ref == "":
        raise InvalidDataOperationException("Invalid plural reference.")
    if deleted_id == None or deleted_id == "":
        raise InvalidDataOperationException("No ID provided.")

    if isinstance(item, dict):
        # Check for singular references and remove them
        if singular_ref in item and item[singular_ref] == deleted_id:
            del item[singular_ref]
        # Check for plural references and remove them
        if plural_ref in item and deleted_id in item[plural_ref]:
            item[plural_ref].remove(deleted_id)

        # Recursively check nested structures
        for key, value in item.items():
            __validate_and_remove_dangling_references_recursive(value, singular_ref, plural_ref, deleted_id)
    elif isinstance(item, list):
        for i in item:
            __validate_and_remove_dangling_references_recursive(i, singular_ref, plural_ref, deleted_id)

def __validate_and_remove_dangling_references_general(data, deleted_id, resource):
    """
    Method that validates and removes references of a deleted item from all other data.
    
    Parameters
    ----------
    data: dict
        The full data dictionary.
    deleted_id: int
        The ID of the deleted item.
    resource: str
        The name of the resource.
    ----------

    Returns
    ----------
    dict
        The updated data dictionary.
    ----------
    """

    if data == None or data == {}:
        raise DataEmptyException("No data provided.")
    if deleted_id == None or deleted_id == "":
        raise InvalidDataOperationException("No ID provided.")
    if resource == None or resource == "":
        raise InvalidDataOperationException("No resource provided.")
    
    # Determine the singular form of the resource
    singular_form = resource[:-1] if resource.endswith('s') else resource
    singular_ref = singular_form + "_id"
    plural_ref = singular_form + "_ids"

    # Iterate over all resources in the data
    for key, items in data.items():
        # Check each item in the resource
        for item in items:
            __validate_and_remove_dangling_references_recursive(item, singular_ref, plural_ref, deleted_id)

    return data
