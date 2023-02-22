import websockets
import socket
import asyncio
import sys

ws = []
r = []
w = []

async def soc_server(r, w):
    global ws
    if (r not in globals()["r"]) or (w not in globals()["w"]):
        globals()["r"].append(r)
        globals()["w"].append(w)
        print("New connection: ", r, w)
    err_count = 0
    while True:
        if w.is_closing():
            globals()["r"].remove(r)
            globals()["w"].remove(w)
            print(r, w, "was closed")
            break
        try:
            rdata = (await r.readline()).decode()
            if rdata == '' and err_count < 1:
                err_count += 1
            elif rdata == '' and err_count == 1:
                print(r, w, "was closed")
                break
            print(rdata)
        except RuntimeError as e:
            print(e)
            rdata = ''
        async def soc_for_loop(x):
            global ws
            if x.closed:
                ws.remove(x)
                return
            try:
                print("sending")
                await x.send(rdata)
                print("sent")
            except websockets.exceptions.ConnectionClosedOK:
                print("woops")
                return
        await asyncio.gather(*[soc_for_loop(x) for x in ws])

async def wss_server(ws):
    global r, w
    globals()["ws"].append(ws)
    ws.legacy_recv = True
    print("New connection: ", ws)
    while True:
        if ws.closed:
            globals()["ws"].remove(ws)
            print(ws, "was closed")
            break
        ws.current_task = asyncio.create_task(ws.recv())
        await asyncio.sleep(0.1)
        try:
            message = await ws.current_task
        except RuntimeError:
            ws.current_task.exception()
            continue
        if message != None:
            print("New message: ", message)
            async def wss_for_loop(x, y):
                if y.is_closing():
                    r.remove(x)
                    w.remove(y)
                    return
                y.write(message.encode())
                try:
                    await y.drain()
                except ConnectionResetError:
                    return
            await asyncio.gather(*[wss_for_loop(x, y) for x, y in zip(r, w)])

async def main():
    if sys.argv[-1] != "-v":
        def fakeprint(*args, **kwargs):
            pass
        globals()["print"] = fakeprint # I AM NOT REWRITING EVERY PRINT STATEMENT IN MY CODE
    server = await asyncio.start_server(soc_server, "127.0.0.1", 16388)
    async with websockets.serve(wss_server, "localhost", 16384), server:
        await server.serve_forever()
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())
