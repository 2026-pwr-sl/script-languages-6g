class HTTPRequest:
    """Simple class representing an HTTP request."""

    def __init__(self, request_type, path, protocol):
        self.request_type = request_type
        self.path = path
        self.protocol = protocol

    def __str__(self):
        return f"{self.request_type} {self.path} {self.protocol}"

    def __repr__(self):
        return (
            f"HTTPRequest({self.request_type!r}, "
            f"{self.path!r}, {self.protocol!r})"
        )


def reqstr2obj(request_string):
    """Function gets text HTTP request and returns HTTP request object."""
    if not isinstance(request_string, str):
        raise TypeError("request_string must be a string")

    parts = request_string.split(" ")

    if len(parts) != 3 or "" in parts:
        return None

    request_type, path, protocol = parts
    return HTTPRequest(request_type, path, protocol)