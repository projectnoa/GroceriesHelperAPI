from controllers.request_controller import handle_request_for

def lambda_handler(event, context):
    """
    Method to handle a request.

    Parameters
    ----------
    event: dict
        The event object containing the request data.
    context: dict
        The context object containing context information.
    ----------

    Returns
    ----------
    dict
        A formatted response object.
    ----------
    """

    return handle_request_for(event)

result = lambda_handler({ "resource": "/dishes", "httpMethod": "GET", "queryStringParameters": {}, "multiValueQueryStringParameters": {} }, {})

print(result)