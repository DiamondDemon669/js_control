class Error(Exception):
    pass

class DOMError(Error):
    pass

class EvalError(Error):
    pass

class MediaError(Error):
    pass

class OverconstrainedError(Error):
    pass

class RangeError(Error):
    pass

class ReferenceError(Error):
    pass

class SyntaxError(Error):
    pass

class TypeError(Error):
    pass

class URIError(Error):
    pass

all_errors = {(getattr(v, "__name__", None) if getattr(v, "__name__", '').endswith('Error') else None): v for k, v in globals().items()}
all_errors.pop(None)
