import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from lab7 import reqstr2obj, HTTPRequest


def test_reqstr2obj_type_error():
    with pytest.raises(TypeError):
        reqstr2obj(123)
        
        
def run_tests():
    test_reqstr2obj_type_error()
    
    
if __name__ == "__main__":
    run_tests()