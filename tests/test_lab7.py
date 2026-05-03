import os
import sys

import pytest

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")),
)

from lab7 import HTTPRequest, reqstr2obj, BadRequestTypeError

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

def test_reqstr2obj_works_with_different_arguments():
        request1 = reqstr2obj("GET /index.html HTTP1.1")
            request2 = reqstr2obj("POST /login HTTP2.0")
                request3 = reqstr2obj("HEAD /status HTTP1.0")

                    assert request1.request_type == "GET"
                        assert request1.path == "/index.html"
                            assert request1.protocol == "HTTP1.1"

                                assert request2.request_type == "POST"
                                    assert request2.path == "/login"
                                        assert request2.protocol == "HTTP2.0"

                                            assert request3.request_type == "HEAD"
                                                assert request3.path == "/status"
                                                    assert request3.protocol == "HTTP1.0"


                                                    def test_reqstr2obj_returns_none_for_wrong_number_of_words():
                                                        assert reqstr2obj("GET /") is None
                                                            assert reqstr2obj("GET / HTTP1.1 extra") is None
                                                                assert reqstr2obj("GET") is None


                                                                def test_reqstr2obj_raises_bad_request_type_error():
                                                                    with pytest.raises(BadRequestTypeError):
                                                                            reqstr2obj("DOWNLOAD /movie.mp4 HTTP1.1")