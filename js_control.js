// ==UserScript==
// @name        js_control
// @namespace   js_control
// @author      DiamondDemon
// @description Remotely controls browser
// @include     *
// @version     1.0.0
// ==/UserScript==

//Websocket constants, can be used by python
let ws
let tabdata
let send = (data) => {
    ws.send(data)
}
//

let ws_init = (event) => {
    tabdata = JSON.parse(JSON.stringify({"url": document.location.href, "title": document.title}))
    var initdata = JSON.stringify({"type": "meta", "data": tabdata})
    send(initdata)
    console.log(initdata)
}

let ws_message = (event) => {
    try {
        var msg = JSON.parse(event.data)
    } catch(err) {
        return
    }
    console.log(msg)
    if (msg === {}) {
        return
    } else if (msg.type === "meta") {
        console.log("command detected")
        if ( !(msg.data.command) ) {
            return
        } else if (msg.data.command === "resend_info") {
            send(JSON.stringify({"type": "meta", "data": tabdata}) + '\n')
        } else if (msg.data.command === "ping" && msg.tab.url === tabdata.url) {
            console.log("hello")
            send(JSON.stringify({"type": "meta", "tab": tabdata, "data": "pong"}))
        }
    } else if ( (!(msg.tab)) || (msg.tab.url !== tabdata.url) ) {
        return
    } else if (msg.type === "data" && msg.data.script) {
        var tosend
        try {
            tosend = JSON.stringify({"type": "data", "tab": tabdata, "data": {"return": JSON.stringify(eval(msg.data.script)).replace(/(^"|"$)/g, '')}})
        } catch(err) {
            tosend = JSON.stringify({"type": "data", "tab": tabdata, "data": {"error": Error.prototype.toString.call(err)}})
        } finally {
            send(tosend)
            console.log(tosend)
        }
    }
}

ws = new WebSocket("ws://localhost:16384")
ws.addEventListener("open", ws_init)
ws.addEventListener("message", ws_message)
console.log("Started up")
