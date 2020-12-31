// Globals
let g_connection = null;
let g_connection_delay = 500;
const g_message_handlers = {};

// Public Functions
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


export function connect()
{
    g_connection = new WebSocket("wss://miramontes.dev:14501");
    g_connection.onopen = on_connect;
    g_connection.onmessage = on_message;
    g_connection.onerror = on_error;
    g_connection.onclose = on_error;
}

export function send(message)
{
    g_connection.send(JSON.stringify(message));
}

export function request(message)
{
    // Ensure request ID
    if (!message.requestId) message.requestId = Math.floor(Math.random() * 4294967294) + 1;

    // Add request to the active requests and send the message
    return new Promise(resolve => {
        g_active_requests[message.requestId] = resolve;
        send(message);
    });
}

// Handlers
function dispatch(message)
{
    if (message.requestId)
    {
        const callback = g_active_requests[message.requestId];
        if (callback)
        {
            callback(message);
        }
        else
        {
            console.error("Ignored request", message);
        }
        return;
    }

    if (message.type == "error")
    {
        console.error("[Server-Error]", message.data);
    }
    else if (message.type == "debug")
    {
        console.warn("[Server-Debug]", message.data);
    }
    else if (message.type in g_message_handlers)
    {
        for (let message_handler of g_message_handlers[message.type]) {
            message_handler(message);
        }
    }
    else
    {
        console.error("Unhandled message", message);
    }
}

async function on_connect()
{
    send({type: "connect"});
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
    // Close connection
    g_connection.onopen = undefined;
    g_connection.onmessage = undefined;
    g_connection.onerror = undefined;
    g_connection.onclose = undefined;
    g_connection = null;
    // Sleep
    await new Promise(resolve => setTimeout(resolve, g_connection_delay));
    // Re-connect
    connect();
}
