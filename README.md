# JS wrapper for python

This project allows you to control browser tabs from python (also nodejs terminal, coming soon)

Tested on Chrome 96, Firefox 108 on Linux and Windows x86 with Tampermonkey

Also tested on KDE Falkon :)

There are a few known bugs, which I am working on

## How to use

1. Clone the repo

2. Run setup.py to install module

3. Install websockets module and run coordinator.py server

4. Install Tampermonkey and load the script js_control.js

5.
```python
import javascript as js
tabdata = {"url": "URL OF TAB", "title": "TITLE OF TAB"} # Data used to identify tab
tab = js.WSSTab("127.0.0.1", 16388, tabdata) # Connect to browser tab
document = js.Object("document", tab) # Locate document object on tab

myelement = document.createElement('"p"')
document.body.appendChild(myelement._name) # _name contains the javascript variable name
myelement.innerHTML = '"I ran javascript"' # You must surround a string in two sets of quotes
```
Notice that the string on the last line is surrounded in two pairs of quotes.
This is because one pair will refer to a javascript variable name, not a string literal
If you need help with this, use the function `js.stringify(string)`
This does not apply to integers

## Data model

All messages between python and the browser are co-ordinated by the coordinator.

It operates a websocket server on port 16384 and a socket server on port 16388

Messages are sent in JSON with scripts sent as 
`{"type": "data", "tab": {"url": "<Tab URL>", "title": "<Tab title>"}, "data": {"script": "<Script to execute, uses eval sorry>"}}`

The browser will then return the following JSON data
`{"type": "data", "tab": {"url": "<Tab URL>", "title": "<Tab title>"}, "data": {"return": "<Data returned>"}}`

If an error occurs, this message will be sent
`{"type": "data", "tab": {"url": "<Tab URL>", "title": "<Tab title>"}, "data": {"error": "<Exception, fresh out of a try ... catch>"}}`

When a tab connects it will send this
`{"type": "meta", "data": {"url": "<Tab URL>", "title": "<Tab title>"}}`

Finally commands are sent using this format. Their return data will be shown in the commands section
`{"type": "meta", "tab": OPTIONAL, "data": {"command": "<command>"}}`
OR
`{"type": "meta", "tab": OPTIONAL, "data": {"command": ["<command>", "<arg1>", "<arg2>", ...]}}`

## Commands

"resend_info": Runs on all tabs. Forces them to resend their tabdata

"ping": Just returns "pong". Runs on specified tab

## Docs

### javascript.variable

#### class Variable

##### _name

String containing reference to javascript variable

##### _tab

Tab object. Inherits from BaseTab

##### _def

Original definition of javascript variable. usually a function call

##### def __new__(self, name, tab, once=False)

If you manage to create an instance of this class, something went seriously wrong.

Locates a variable on tab. If once is True, a new variable will be created

##### def __init_subclass__(cls, jstype, **kwargs)

This is used when inheriting from Variable. jstype is the type given from typeof x in javascript. 
Dont know why it edits the registry of Variable

##### def __getattr__, __setattr__, __delattr__

Gets, sets or deletes attribute on javascript variable. Does not require two pairs of quotes, except for setting attribute value

##### def __getitem__, __setitem__, __delitem__

Gets, sets or deletes item on javascript variable. Requires two pairs of quotes

##### def __repr__

Returns <{self.__class__.__module__}.{self.__class__.__name__} {self._name or self._def} at {hex(id(self))}>

##### def __str__

Returns self._name or self._def if applicable

##### def __bytes__

Returns str(self).encode()

##### def __bool__

Returns (self._tab.send_script(f"String(!!{self._name})") == "true")

### javascript.primitives

#### class Undefined, Symbol, Object, Boolean, BigInt

Returned from javascript.variable.Variable.__new__ when JS variable referred to corresponds to type. No special functions

#### class Function(Variable, jstype="function")

##### def __call__(self, *args, **kwargs)

The really interesting part! Parses args and kwargs into string literal and returns Variable with function call as _def

Creates a new variable on javascript end using once=True

#### class Number(Variable, jstype="number")

##### def __int__(self)

Just returns integer representation of itself

#### class String(Variable, jstype="string")

##### def __str__(self)

Just returns string representation of itself

### javascript.errors

Im not writing that. if you want to see, just look at javascript.errors.all_errors

### javascript.utils

#### def rand_string(l=6)

Generates a random string. used by Variable to generate new variable name

#### def stringify(string)

For those who cannot write f'"{string}"'

#### def object_type(obj)

Gets the real type of a JS object. uses Object.prototype.toString.call

### javascript.communication

#### class BaseTab

All tab objects must inherit from this

##### def send_script(self, data, fdata=None)

##### def start_callback(self, func)

##### def stop_callback(self, func)

#### class StdIOTab(BaseTab)

Used for testing. Instead of sending JS to browser, it will run input()

#### class WSSTab(BaseTab)

The default tab. Connects to co-ordinator

##### def __init__(self, host, port, tabdata, ping=True)

Just sets up variables, will only connect to ping tab unless ping is False

##### def __repr__(self)

Returns f"{self.__class__.__name__}({self.connection[0]}, {self.connection[1]}, {self.tabdata})"

##### def send_json(self, data)

Sends raw JSON data. Use send_script with fdata instead

##### def send_script(self, data, fdata=None)

Sends javascript. will return the JS data or raise an error corresponding to JS errors

##### def start_callback(self, func)

Allows javascript to call python functions. Not done yet, so do not use

##### def stop_callback(self, func)

Also not done yet

##### classmethod async def async_get_tabs(cls, host, port, url_search, title_search)

Forces all tabs to resend data, returns list of WSSTab.
URL search and title search not implemented, do not use

##### classmethod def get_tabs(cls, host="127.0.0.1", port=16388, url_search='', title_search='')

Just calls the function described above

#### class NodeTab(BaseTab)

Definently not done yet, only works on linux due to broken pty module
