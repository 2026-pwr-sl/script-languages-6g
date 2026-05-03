import pytest


class HTTPRequest:
    def __init__(self, request_type, path, protocol):
        self.request_type = request_type
        self.path = path
        self.protocol = protocol
        
        
def reqstr2obj(request_string):
    """Function gets text HTTP request and returns HTTP request object"""
    pass


def test_reqstr2obj_type_error():
    with pytest.raises(TypeError):
        reqstr2obj(123)
        
        
def run():
    test_reqstr2obj_type_error()
    

if __name__ == "__main__":
    run()