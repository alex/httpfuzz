# `httpfuzz`

`httpfuzz` is a project which wires libFuzzer (via Atheris) to WSGI in order to
use fuzzing to look for bugs and vulnerabilities.

At the moment this is more of a tech-demo than something likely to find a ton
of vulnerabilities, but perhaps you'll send a PR to extend it or be inspired to
build something even better.


## How to use it

`httpfuzz` requires that you have `werkzeug` and `atheris` installed.

See `example/demoapp.py` for a complete example, but in short:

```py
import httpfuzz

httpfuzz.fuzz(wsgi_app)
```

## Limitations

### Regular expression coverage

Because of how Atheris/libFuzzer work, by default no coverage data is collected
of `_sre` (the Python module that implements the regular expression engine).
This means that left to its own devices, `httpfuzz` is unlikely to find inputs
that satisfy a regexp. Because many Python web frameworks use regular
expressions for URL routing this is a problem. The solution (for now) is to
generate a libFuzzer dictionary of components from URLs.

The `example/` directory contains an example dictionary (`re.dict`) for
`demoapp.py`. It also contains `re_extract.py` which can generate values for a
dictionary from regexp objects. They can then be passed to the fuzzer:

```console
$ python demoapp.py -dict=re.dict
```

### HTTP features

`httpfuzz` currently only generates request URLs and different HTTP methods. It
does not generate request bodies or headers. These should be straight forward
to add.

### State

Consider a web app with routes for creating, updating, and destroying a
resource in a database. It would be very easy to end up with a
non-deterministic because whether a request to the update route received a 404
or not would depend on whethter the fuzzer had generated a create request (but
not a destroy request) previously!

The correct way to handle that is probably to have the fuzzer generate
*sequences* of HTTP requests, and resetting state in between executions. This
would allow you to create deterministic sequences of create followed by update
requests.

In a similiar vein, `httpfuzz` would probably benefit from some sort of hook
which allowed injection of things like authentication.

### Sanitizers

One of the reasons that libFuzzer is effective against C codebases is because
the sanitizers ensure that vulnerabilities are caught promptly. To be equally
impactful, an equivilant set of sanitizers is required for `httpfuzz`.

Currently `httpfuzz` merely checks that the WSGI app does not raise an
exception or return a 5xx response. These will catch some vulnerability
classes, e.g.:

- SQL injection is likely to be caught because malformed injections will raise
  exceptions
- Command injection is similarly likely to be caught

However, there are a number of other bug classes which could be caught, if we
had sanitizers for them:

- Checking that HTML responses are well-formed could catch XSS.
- Checking for attempts to open files outside of a pre-specified root could
  catch path traversal vulnerabilities.
