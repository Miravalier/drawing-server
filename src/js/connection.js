import * as utils from "./utils.js";

// Globals
let g_token = null;
let g_connection = null;
const g_connection_delay = 2500;
const g_request_timeout = 15000;
const g_timeout_poll_rate = 3000;
const g_message_handlers = {};
const g_waiting_messages = {};
const g_heartbeat_rate = 3000;

// Public Functions
export function init()
{
    // Go through and timeout abandoned requests
    setInterval(() => {
        const currentTime = Date.now();
        const timeouts = [];
        for (let [message, resolve, timeout] of Object.values(g_waiting_messages))
        {
            if (currentTime > timeout)
            {
                timeouts.push([message.id, resolve]);
            }
        }
        for (let [id, resolve] of timeouts)
        {
            delete g_waiting_messages[id];
            resolve(Promise.reject(new Error("request timed out")));
        }
    }, g_timeout_poll_rate);

    // Send a heartbeat to avoid getting timed out
    setInterval(() => {
        if (g_connection && g_connection.readyState == WebSocket.OPEN)
        {
            send({type: "heartbeat"});
        }
    }, g_heartbeat_rate);
}


export function on(type, handler)
{
    // Get handlers array
    const handlers = g_message_handlers[type] || [];
    g_message_handlers[type] = handlers;

    // Add this handler
    handlers.push(handler);
}


export async function once(type, handler)
{
    // Ensure there is a handler - useful if the caller awaits the message
    if (handler === undefined) handler = (() => {});

    // Get handlers array
    const handlers = g_message_handlers[type] || [];
    g_message_handlers[type] = handlers;

    // Add this handler
    handlers.push(handler);

    // Wait for the handler to be called
    const message = await new Promise(resolve => {
        handlers.push(resolve)
    });

    // Remove this handler
    handlers.splice(handlers.indexOf(handler), 1);

    // Return the message we're waiting for
    return message;
}


export function off(type, handler)
{
    // Get handlers array
    const handlers = g_message_handlers[type] || [];
    g_message_handlers[type] = handlers;

    // Remove this handler
    handlers.splice(handlers.indexOf(handler), 1);
}


export function reconnect()
{
    g_connection = new WebSocket(WSS_URL);
    g_connection.onopen = on_reconnect;
    g_connection.onmessage = on_message;
    g_connection.onerror = on_error;
    g_connection.onclose = on_error;
}


export function connect()
{
    // Get id from localstorage
    if (g_token === null)
    {
        g_token = localStorage.getItem("token");
        // Put id into localstorage if there isn't one
        if (g_token === null)
        {
            g_token = utils.token(16);
            localStorage.setItem("token", g_token);
        }
    }
    g_connection = new WebSocket(WSS_URL);
    g_connection.onopen = on_connect;
    g_connection.onmessage = on_message;
    g_connection.onerror = on_error;
    g_connection.onclose = on_error;
}


export async function send(message)
{
    // Ensure request ID
    if (!message.id) message.id = utils.randInt();

    // Add request to the active requests and send the message
    return new Promise(resolve => {
        const timeout = Date.now() + g_request_timeout;
        g_waiting_messages[message.id] = [message, resolve, timeout];
        g_connection.send(JSON.stringify(message));
    });
}


// Handlers
export function dispatch(message)
{
    if (message.type === "error")
    {
        console.error("[Server-Error]", message.data);
    }
    else if (message.type === "debug")
    {
        console.warn("[Server-Debug]", message.data);
    }
    else if (message.type in g_message_handlers)
    {
        for (let message_handler of g_message_handlers[message.type]) {
            message_handler(message);
        }
    }

    if (message.id in g_waiting_messages)
    {
        const [request, resolve, timeout] = g_waiting_messages[message.id];
        resolve(message);
        delete g_waiting_messages[message.id];
    }
}


async function on_reconnect()
{
    g_connection.send(JSON.stringify({type: "reconnect", token: g_token}));
    for (let [message, resolve, timeout] of Object.values(g_waiting_messages))
    {
        g_connection.send(JSON.stringify(message));
    }
}


async function on_connect()
{
    g_connection.send(JSON.stringify({type: "connect", token: g_token}));
    for (let [message, resolve, timeout] of Object.values(g_waiting_messages))
    {
        g_connection.send(JSON.stringify(message));
    }
}


async function on_message(event)
{
    if (event.data instanceof Blob) {
        const buffer = await event.data.arrayBuffer();
        const view = new DataView(buffer);
        const type = view.getUint32(0);
        const data = new Uint8Array(buffer, 4, buffer.byteLength - 4);
        await dispatch({type, data});
    }
    else if (event.data instanceof ArrayBuffer) {
        const view = new DataView(event.data);
        const type = view.getUint32(0);
        const data = new Uint8Array(buffer, 4, buffer.byteLength - 4);
        await dispatch({type, data});
    }
    else {
        // Parse JSON message
        let message = null;
        try {
            message = JSON.parse(event.data);
        }
        catch (e) {
            console.error("WSS message is not valid JSON", event.data);
            return;
        }
        // Ensure message has a type
        if (!message.type) {
            console.error("WSS message missing type", event.data);
            return;
        }
        // Dispatch
        await dispatch(message);
    }
}


async function on_error()
{
    console.log("Connection to server lost. Reconnecting ...");
    // Close connection
    g_connection.onopen = undefined;
    g_connection.onmessage = undefined;
    g_connection.onerror = undefined;
    g_connection.onclose = undefined;
    g_connection = null;
    // Sleep
    await new Promise(resolve => setTimeout(resolve, g_connection_delay));
    // Re-connect
    reconnect();
}
