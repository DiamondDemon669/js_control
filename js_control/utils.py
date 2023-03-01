import random, string, json

Variable = None # Set in __init__, used by stringify

def rand_string(l=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=l))

def stringify(string):
    if isinstance(Variable, None.__class__):
        raise ImportError("Module was not imported correctly")
    if isinstance(string, Variable):
        return string._name
    elif isinstance(string, str):
        return f'"{string}"'
    elif isinstance(string, dict) or isinstance(string, list):
        return json.dumps(string)
    elif isinstance(string, bool):
        return str(string).lower()
    else:
        return str(string)

def object_type(obj):
    f = obj._registry["function"]("Object.prototype.toString.call", obj._tab)
    return str(f(obj._name)).strip("[]").replace("object ", '')

