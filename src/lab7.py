class HTTPRequest:
    def __init__(self, request_type, path, protocol):
        self.request_type = request_type
        self.path = path
        self.protocol = protocol
        
    def __str__(self):
        return f"{self.request_type} {self.path} {self.protocol}"
        
        
def reqstr2obj(request_string):
    """Function gets text HTTP request and returns HTTP request object"""
    if not isinstance(request_string, str):
        raise TypeError(f"Expected str, got {type(request_string).__name__}")
    
    parts = request_string.strip().split()
    if len(parts) < 3:
        raise ValueError("Invalid request format")
    
    request_type = parts[0]
    path = parts[1]
    protocol = parts[2]
    
    return HTTPRequest(request_type, path, protocol)
