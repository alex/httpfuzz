from werkzeug.exceptions import HTTPException
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Request, Response

import httpfuzz

class WebApp(object):
    def __init__(self):
        self.url_map = Map([
            Rule(r"/test/<name>/", endpoint=self.test),
            Rule(r"/", endpoint=self.home),
        ])

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self.handle_request(request)
        return response(environ, start_response)

    def handle_request(self, request):
        adapter = self.url_map.bind_to_environ(request)
        try:
            endpoint, args = adapter.match()
            return endpoint(request, **args)
        except HTTPException as e:
            return e

    def home(self, request):
        return Response("Hello World!")

    def test(self, request, name):
        if name == "foobar":
            raise ZeroDivisionError
        return Response("Hello " + name)


if __name__ == "__main__":
    httpfuzz.fuzz(WebApp())
