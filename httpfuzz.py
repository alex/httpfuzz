import sys
import urllib.parse

import atheris

from werkzeug.urls import iri_to_uri
from werkzeug.test import Client
from werkzeug.wrappers import BaseResponse


def fuzz_request(data, wsgi_app):
    fdp = atheris.FuzzedDataProvider(data)

    method = fdp.PickValueInList(["GET", "POST", "PUT", "HEAD", "DELETE", "OPTIONS", "TRACE", "PATCH"])

    url_length = fdp.ConsumeUInt(2)
    url = urllib.parse.quote(fdp.ConsumeBytes(url_length), safe='/?&=%')

    c = Client(wsgi_app, BaseResponse)
    resp = c.open(path=url, method=method)
    assert not (500 <= resp.status_code <= 599)


def fuzz(wsgi_app):
    atheris.Setup(sys.argv, lambda data: fuzz_request(data, wsgi_app), enable_python_coverage=True)
    atheris.Fuzz()
