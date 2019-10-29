from flask import request


JSON_MIME = "application/json"
JSONAPI_MIME = "application/vnd.api+json"


def requested_type():
    """Get requested response mime-type."""
    try:
        return request.headers.get("Accept", JSON_MIME)
    except RuntimeError:  # Called outside request context
        return JSON_MIME


def jsonapi_requested():
    """
    Check whether the requester explicitly requested a response in the
    JSON:API format.
    """
    return requested_type() == JSONAPI_MIME
