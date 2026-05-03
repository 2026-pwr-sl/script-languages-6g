class HTTPRequest:
    def __init__(self, request_type, path, protocol):
        self.request_type = request_type
        self.path = path
        self.protocol = protocol
        
    def __str__(self):
        return f"{self.request_type} {self.path} {self.protocol}"
        
        
def reqstr2obj(request_string):
    """Function gets text HTTP request and returns HTTP request object"""
    pass


