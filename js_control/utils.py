import random, string

def rand_string(l=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=l))

def stringify(string):
    return f'"{string}"'

def object_type(obj):
    f = obj._registry["function"]("Object.prototype.toString.call", obj._tab)
    return str(f(obj._name)).strip("[]").replace("object ", '')

