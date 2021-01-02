from game import Lobby, Player
from status import *

# Global table of message types to handlers
request_handlers = {}


class InvalidParameter(Exception):
    pass


# Register decorator
def register(message_type, arguments=None):
    if arguments is None:
        arguments = []

    def validator(message):
        for name, cls in arguments:
            value = message.get(name, InvalidParameter)
            if value is InvalidParameter:
                raise InvalidParameter(
                    "{} request missing required parameter: '{}'".format(
                        message_type,
                        name
                    )
                )
            elif not isinstance(value, cls):
                raise InvalidParameter(
                    "{} parameter '{}' must be of type '{}', not '{}'".format(
                        message_type,
                        name,
                        cls.__name__,
                        type(value).__name__
                    )
                )

    def handler(func):
        request_handlers[message_type] = (validator, func)
        return func

    return handler


############
# Handlers #
############


@register("ping")
async def on_ping(ctx):
    info("Received ping:", ctx.message, "from", ctx.requester);
    ctx.message["type"] = "pong"
    return ctx.message


@register("createLobby", [('name', str), ('public', bool)])
async def on_create_lobby(ctx):
    # Validate length
    if len(ctx.message['name']) == 0:
        return "player name must be at least 1 character long"

    # Create lobby
    lobby = Lobby.create(Player(ctx.requester, ctx.message['name']), ctx.message['public'])

    # Send broadcast
    if lobby.public:
        await ctx.broadcast({"type": "lobbyCreated", "owner": lobby.owner.data})
