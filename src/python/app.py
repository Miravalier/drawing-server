import asyncio
import random
import secrets
import string
from task import task
from handler import register
from messages import *


########
# Init #
########


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

    def __init__(self, public=False, owner=None):
        self.public = public

        self.players = set()
        self.owner = owner

        # Generate an unused join code
        self.join_code = "".join(random.choice(string.ascii_letters) for _ in range(8))
        while self.join_code in Lobby.lobbies:
            self.join_code = "".join(random.choice(string.ascii_letters) for _ in range(8))

        Lobby.lobbies[self.join_code] = self

    def remove(self, ctx):
        # Remove this player
        self.players.discard(ctx)

        # If no one is left, delete the lobby
        if len(self.players) == 0:
            del Lobby.lobbies[self.join_code]

        # If this player was the owner, pick a new one
        elif ctx is self.owner:
            self.owner = random.choice(self.players)


#############
# Functions #
#############


def color(value):
    if not isinstance(value, str):
        raise TypeError("colors must be strings in the form #xxxxxx")
    if not re.fullmatch("#[0-9a-fA-F]{6}"):
        raise ValueError("colors must match the form #xxxxxx")
    return value.lower()


def random_color():
    return "#{:02x}{:02x}{:02x}".format(
        secrets.randbelow(256),
        secrets.randbelow(256),
        secrets.randbelow(256)
    )


############
# Handlers #
############


@register("connect")
async def on_connect(ctx, message):
    """
    Called whenever a user connects.
    """
    ctx.lobby = None
    ctx.name = "Guest"
    ctx.color = random_color()

    return {"type": "connected"}


@register("reconnect")
async def on_reconnect(ctx, message):
    """
    Called whenever a user reconnects.
    """
    return {"type": "reconnected"}


@register("disconnect")
async def on_disconnect(ctx, message):
    """
    Called whenever a user doesn't communicate for 60 seconds,
    or if the user sends this request specifically.
    """
    # Leave the player's lobby
    if ctx.lobby:
        ctx.lobby.remove(ctx)


@register("createLobby", [('public', bool)])
async def on_create_lobby(ctx, message):
    """
    Creates a lobby and returns the join code.
    """
    if ctx.lobby:
        ctx.lobby.remove(ctx)

    # Create lobby
    lobby = Lobby(message['public'], ctx)
    ctx.lobby = lobby

    reply = {
        "type": "lobbyCreated",
        "joinCode": lobby.join_code,
        "players": len(lobby.players),
        "ownerName": lobby.owner.name
    }

    # Send broadcast
    if lobby.public:
        await ctx.broadcast(reply);

    return reply


@register("setName", [('name', str)])
async def on_set_name(ctx, message):
    # Validate length
    if len(message['name']) == 0:
        return "player name must be at least 1 character long"
    # Store name
    ctx.name = message['name']


@register("setColor", [('color', color)])
async def on_set_color(ctx, message):
    ctx.color = color


@register("joinLobby", [('joinCode', str)])
async def on_join_lobby(ctx, message):
    """
    Leaves the user's current lobby and joins a new lobby.
    """
    if ctx.lobby:
        ctx.lobby.remove(ctx)
    lobby = Lobby.lobbies[message['joinCode']]
    lobby.players.add(ctx)
    ctx.lobby = lobby

    reply = {
        "type": "lobbyJoined",
        "joinCode": lobby.join_code,
        "players": len(lobby.players),
        "ownerName": lobby.owner.name
    }

    return reply


@register("leaveLobby")
async def on_leave_lobby(ctx, message):
    """
    Leaves the user's current lobby.
    """
    if ctx.lobby:
        ctx.lobby.remove(ctx)

    reply = {
        "type": "lobbyLeft",
    }

    return reply


@register("getLobbies")
async def on_get_lobbies(ctx, message):
    """
    Returns a list of active public lobbies.
    """
    return {
        "type": "lobbyList",
        "lobbies": [
            {
                "joinCode": lobby.join_code,
                "players": len(lobby.players),
                "ownerName": lobby.owner.name
            }
            for lobby in Lobby.lobbies.values()
            if lobby.public
        ]
    }
