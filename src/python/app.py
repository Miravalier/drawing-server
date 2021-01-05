import asyncio
import random
import string
from task import task
from handler import register
from messages import *


# Init Function
async def init():
    pass


####################
# Background Tasks #
####################


###########
# Classes #
###########


class Lobby:
    lobbies = {}

    def __init__(self, public):
        self.public = public

        self.players = []
        self.join_code = "".join(random.choice(string.ascii_letters) for _ in range(8))

        Lobby.lobbies[self.join_code] = self


############
# Handlers #
############


@register("connect")
async def on_connect(ctx, message):
    """
    Called whenever a user connects or reconnects.
    """
    if not hasattr(ctx, "lobby"):
        ctx.lobby = None

    return {"type": "connected"}


@register("createLobby", [('public', bool)])
async def on_create_lobby(ctx, message):
    """
    Creates a lobby and returns the join code.
    """
    # Validate length
    if len(message['name']) == 0:
        return "player name must be at least 1 character long"

    # Create lobby
    lobby = Lobby(message['public'])

    reply = {
        "type": "lobbyCreated",
        "joinCode": lobby.join_code
    }

    # Send broadcast
    if lobby.public:
        await ctx.broadcast(reply);

    return reply;


@register("getLobbies")
async def on_get_lobbies(ctx, message):
    """
    Returns a list of active public lobbies.
    """
    return {
        "type": "lobbyList",
        "lobbies": [
            {"joinCode": lobby.join_code, "players": len(lobby.players)}
            for lobby in Lobby.lobbies.values()
            if lobby.public
        ]
    }


@register("heartbeat")
async def on_heartbeat(ctx, message):
    """
    Used to update the last_checkin and keep the connection alive.
    """
    pass
