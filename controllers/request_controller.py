import json

from controllers.data_controller import DataException, DataNotFoundException, DataEmptyException, S3NotAvailableException, InvalidDataOperationException, get_data, add_data_to, edit_data_for, delete_data_for, retrieve_referenced_entities

class RequestException(Exception):
    pass

class InvalidRequestException(RequestException):
    pass

class InvalidMethodException(RequestException):
    pass

class InvalidResourceException(RequestException):
    pass

class InvalidEntityException(RequestException):
    pass

def __handle_request(event):
    """
    Method to handle a request.

    Parameters
    ----------
    event: dict
        The event object containing the request data.
    ----------

    Returns
    ----------
    dict
        A formatted response object.
    ----------
    """

    # Get full data from S3
    data = get_data()

    if event is None:
        raise InvalidRequestException("Request is invalid.")
    if "httpMethod" not in event:
        raise InvalidMethodException("Request method is invalid.")
    if "resource" not in event:
        raise InvalidResourceException("Request resource is invalid.")
    if "queryStringParameters" not in event:
        raise InvalidEntityException("Request entity is invalid.")
    # Get request data
    method = event["httpMethod"]
    query_string_data = event["queryStringParameters"]
    resourse_data = event["resource"]
    # multi_value_query_string_data = event["multiValueQueryStringParameters"]
    if resourse_data is None or len(resourse_data) <= 3 or resourse_data[1:] not in data["data"]:
        raise InvalidResourceException("Request resource is invalid.")
    # Split the resource to detect potential IDs
    resource_parts = resourse_data[1:].split('/')
    resource = resource_parts[0]
    entity_id = int(resource_parts[1]) if len(resource_parts) > 1 else None
    # Initialize result
    result = {}
    # Parse request
    match method:
        case "GET":
            if entity_id:
                # Retrieve a single entity based on the ID
                entity = next((item for item in data["data"][resource] if item["id"] == entity_id), None)
                # Raise exception if entity not found
                if entity:
                    result = entity
                else:
                    raise DataNotFoundException(f"{resource} with ID {entity_id} not found.")
            else:
                result = data["data"][resource]
        case "POST":
            result = add_data_to(data, query_string_data, resource)
        case "PUT":
            result = edit_data_for(data, query_string_data, resource)
        case "DELETE":
            result = delete_data_for(data, query_string_data["id"], resource)
        case _:
            result = __build_response("Invalid method")
    # Return result
    return __build_response(retrieve_referenced_entities(result, data["data"]))

def handle_request_for(event):
    """
    Method to handle a request.

    Parameters
    ----------
    event: dict
        The event object containing the request data.
    ----------

    Returns
    ----------
    dict
        A formatted response object.
    ----------
    """

    try:
        return __handle_request(event)
    except InvalidRequestException as ex:
        return __build_response(__build_error(str(ex)), 400)
    except InvalidMethodException as ex:
        return __build_response(__build_error(str(ex)), 405)
    except InvalidResourceException as ex:
        return __build_response(__build_error(str(ex)), 400)
    except InvalidEntityException as ex:
        return __build_response(__build_error(str(ex)), 400)
    except DataNotFoundException as ex:
        return __build_response(__build_error(str(ex)), 404)
    except DataEmptyException as ex:
        return __build_response(__build_error(str(ex)), 400)
    except S3NotAvailableException as ex:
        return __build_response(__build_error(str(ex)), 500)
    except InvalidDataOperationException as ex:
        return __build_response(__build_error(str(ex)), 400)
    except RequestException as ex:
        return __build_response(__build_error(str(ex)), 400)
    except DataException as ex:
        return __build_response(__build_error(str(ex)), 500)
    except Exception as ex:
        return __build_response(__build_error(f"Unknown Error: \n\n{str(ex)}"), 500)

def __build_error(message):
    """
    Method to build an error message for a response.

    Parameters
    ----------
    message: str
        The error message.
    ----------

    Returns
    ----------
    dict
        A formatted response object.
    ----------
    """

    return { "error": message }

def __build_response(body, status_code = 200):
    """
    Method to build a response.

    Parameters
    ----------
    body: dict
        The body of the response.
    ----------

    Returns
    ----------
    dict
        A formatted response object.
    ----------
    """

    # Build response body
    return {
        "isBase64Encoded": False,
        "statusCode": status_code,
        "headers": { 
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*" 

        },
        "body": json.dumps(body)
    }