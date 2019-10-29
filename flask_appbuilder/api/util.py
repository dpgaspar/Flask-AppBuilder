from flask import request


JSON_MIME = "application/json"


def requested_type():
    """Get requested response mime-type."""
    try:
        return request.headers.get("Accept", JSON_MIME)
    except RuntimeError:  # Called outside request context
        return JSON_MIME
