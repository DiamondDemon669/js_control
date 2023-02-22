from .errors import all_errors
import os, sys, json, asyncio, socket, platform, select

class BaseTab:
    def send_script(self, data, fdata=None):
        raise NotImplemented
    def start_callback(self, func):
        raise NotImplemented
    def stop_callback(self, func):
        raise NotImplemented

class StdIOTab(BaseTab):
    def send_script(self, data, fdata=None):
        return input(data + " > ")

class WSSTab(BaseTab):
    _registry = {}
    def __init__(self, host, port, tab, ping=True):
        self.connection = host, port
        self.tabdata = tab
        if ping:
            ping = json.dumps({"type": "meta", "tab": self.tabdata, "data": {"command": "ping"}}).encode()
            pong = {"type": "meta", "tab": self.tabdata, "data": "pong"}
            ping = self.send_json(ping)
            if ping != pong:
                del self
                raise ConnectionRefusedError("Tab did not return ping")
    def __repr__(self):
        return f"{self.__class__.__name__}({self.connection[0]}, {self.connection[1]}, {self.tabdata})"
    def send_json(self, data):
        s = socket.socket()
        s.connect(self.connection)
        s.setblocking(False)
        s.sendall(data + b"\n")
        ready = select.select([s], [], [], 0.5)
        if ready[0]:
            rdata = s.recv(4096)
        else:
            return {}
        return json.loads(rdata.decode())
    def send_script(self, data, fdata=None):
        fdata = {"tab": self.tabdata, "type": "data", "data": {"script": data}} or fdata
        rdata = self.send_json(json.dumps(fdata).encode())["data"]
        if rdata.get("return"):
            return rdata["return"]
        elif rdata.get("error"):
            err, msg = rdata.split(': ')
            raise all_errors[err](msg)
    def start_callback(self, func): #TODO
        def wrapper():
            nonlocal self, func
            name = func.__name__
            self._registry[func.__name__] = func
            data = """{name} = (TODO) => {{ data = {{"tab": tabdata, "type": "data", "data": {{"callbackExec": "{name}"}}}}
                ws.send(data.toString()) }}""".replace("\n                ", '; ')
            self.send_script(data)
        return wrapper
    def stop_callback(self, name):
        del self._registry[name]
    @classmethod
    async def async_get_tabs(cls, host, port, url_search, title_search):
        r, w = await asyncio.open_connection(host, port)
        data = {"type": "meta", "data": {"command": "resend_info"}}
        w.write(json.dumps(data).encode() + b"\n")
        await w.drain()
        await asyncio.sleep(0.3)
        lines = await r.read(65535)
        tabs = []
        for line in lines.split(b'\n'):
            if not line:
                continue
            line = line.decode()
            tabs.append(cls(host, port, json.loads(line)["data"], ping=False))
        w.close()
        return tabs
    @classmethod
    def get_tabs(cls, host="127.0.0.1", port=16388, url_search='', title_search=''):
        return asyncio.run(cls.async_get_tabs(host, port, url_search, title_search))

class NodeTab(BaseTab): # Im working on it
    def __init__(self, command="node"):
        self._m_fd, self._s_fd = pty.openpty()
        self._proc = subprocess.Popen(command, shell=True, stdin=self._s_fd, stdout=self._s_fd, stderr=self._s_fd)
    def read(bytes=65535):
        return os.read(self._m_fd, bytes)
    def write(data):
        return os.write(self._m_fd, data)

if platform.system() == "Windows":
    NodeTab = None
