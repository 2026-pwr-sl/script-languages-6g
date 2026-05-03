import os
import sys

import pytest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")),
)

from lab7 import HTTPRequest, reqstr2obj


def test_reqstr2obj_type_error():
    with pytest.raises(TypeError):
        reqstr2obj(123)


def test_reqstr2obj_returns_http_request_object():
    request = reqstr2obj("GET / HTTP1.1")

    assert isinstance(request, HTTPRequest)


def test_reqstr2obj_sets_attributes_correctly():
    request = reqstr2obj("GET / HTTP1.1")

    assert request.request_type == "GET"
    assert request.path == "/"
    assert request.protocol == "HTTP1.1"