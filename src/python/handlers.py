from status import *

# Handlers
request_handlers = {}


# Register decorator
def register(message_type):
    def handler(func):
        request_handlers[message_type] = func
        return func
    return handler


@register("connect")
def on_connect(websocket, message):
    return {"type": "connected"}
