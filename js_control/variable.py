from .utils import rand_string, stringify
from .communication import BaseTab

class Variable:
    _registry = {}
    def __init_subclass__(cls, jstype, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._registry[jstype] = cls
    def __new__(cls, name, tab, once=False):
        if not isinstance(tab, BaseTab):
            raise TypeError("Tab must be instance of javascript.communication.BaseTab")
        if once:
            string = rand_string()
            while tab.send_script(f"typeof {string}") != "undefined":
                string = rand_string()
            tab.send_script(f"{string} = {name}")
            definition = name
            name = string
        jstype = tab.send_script(f"typeof {name}")
        subcls = cls._registry[jstype]
        obj = object.__new__(subcls)
        object.__setattr__(obj, "_name", name)
        object.__setattr__(obj, "_tab", tab)
        if once:
            object.__setattr__(obj, "_def", definition)
        return obj
    def __matmul__(self, value):
        return self._tab.send_script(f"{self._name} = {stringify(value)}")
    def __getattr__(self, name):
        if name in object.__getattribute__(self, "__dict__"):
            return object.__getattribute__(self, "__dict__")[name]
        attr = Variable(f"{self._name}.{name}", self._tab)
        if isinstance(attr, self._registry["undefined"]):
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        else:
            return attr
    def __setattr__(self, name, value):
        self._tab.send_script(f"{self._name}.{name} = {stringify(value)}")
    def __delattr__(self, name):
        self._tab.send_script(f"{self._name}.{name} = undefined")
    def __getitem__(self, name):
        item = Variable(f"{self._name}[{stringify(name)}]", self._tab)
        if isinstance(item, self._registry["undefined"]):
            raise KeyError(item)
        else:
            return item
    def __setitem__(self, name, value):
        self._tab.send_script(f"{self._name}[{stringify(name)}] = {stringify(value)}")
    def __delitem__(self, name):
        self._tab.send_script(f"{self._name}[{stringify(name)}] = undefined")
    def __repr__(self):
        objrepr = object.__repr__(self)
        try:
            name = object.__getattribute__(self, "_def")
        except AttributeError:
            name = object.__getattribute__(self, "_name")
        objrepr = objrepr.replace("object", name)
        return objrepr
    def __str__(self):
        try:
            name = object.__getattribute__(self, "_def")
        except AttributeError:
            name = object.__getattribute__(self, "_name")
        return name
    def __bytes__(self):
        return str(self).encode()
    def __bool__(self):
        return (self._tab.send_script(f"String(!!{self._name})") == "true")
