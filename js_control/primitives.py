from .variable import Variable
from .utils import stringify

class Undefined(Variable, jstype="undefined"):
    pass

class Symbol(Variable, jstype="symbol"):
    pass

class Object(Variable, jstype="object"):
    pass

class Function(Variable, jstype="function"):
    def __call__(self, *args, **kwargs):
        args = list(args)
        for x, y in enumerate(args):
            args[x] = stringify(y)
        for x, y in kwargs.items():
            kwargs[x] = stringify(y)
        parsed_args = str(args).strip("[]").replace("\'", '') + (', ' if kwargs else '')
        parsed_args += ", ".join([f"{k}={v}" for k, v in kwargs.items()])
        parsed_args = parsed_args.strip().strip(",").strip()
        return Variable(f"{self._name}({parsed_args})", self._tab, once=True)

class Boolean(Variable, jstype="boolean"):
    pass

class BigInt(Variable, jstype="bigint"):
    pass

class Number(Variable, jstype="number"):
    def __int__(self):
        if not self.__dict__.get("_py_val"):
            object.__setattr__(self, "_py_val", int(self._tab.send_script(self._name)))
        return self._py_val
    def __str__(self):
        return str(int(self))

class String(Variable, jstype="string"):
    def __str__(self):
        if not self.__dict__.get("_py_val"):
            object.__setattr__(self, "_py_val", self._tab.send_script(self._name))
        return self._py_val
