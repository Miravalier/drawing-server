import asyncio
import random
import secrets
import string
from dataclasses import dataclass
from enum import Enum
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


class GameError(Exception):
    pass


class StoryElement:
    pass


@dataclass
class StoryDrawing(StoryElement):
    player: str
    image: str

    def to_dict(self):
        return {'type': 'storyDrawing', 'player': self.player, 'image': self.image}


@dataclass
class StoryCaption(StoryElement):
    player: str
    text: str

    def to_dict(self):
        return {'type': 'storyCaption', 'player': self.player, 'text': self.text}


class LobbyState(Enum):
    FORMING = 1
    PROMPTING = 2
    DRAWING = 3
    CAPTIONING = 4
    REVIEWING = 5


class Lobby:
    lobbies = {}

    def __init__(self, public=False, owner=None):
        self.public = public

        self.players = set()
        self.owner = owner
        self.round_timer = 30

        # Increase as the game progresses
        self.state = LobbyState.FORMING
        self.round = 0

        # Generate an unused join code
        self.join_code = None
        while self.join_code is None or self.join_code in Lobby.lobbies:
            self.join_code = "".join(random.choice(string.ascii_letters) for _ in range(8))

        Lobby.lobbies[self.join_code] = self

    async def state_change(self):
        self.round += 1
        messages = []
        # To reviewing state
        if self.round >= len(self.players):
            self.state = LobbyState.REVIEWING
            for ctx in self.players:
                ctx.prompt = None
                messages.append(ctx.send({
                    "type": "reviewing"
                }))
            # Convert stories from a dictionary to a list
            self.stories = list(self.stories.values())
            self.stories_reviewed = 0
            self.elements_reviewed = 0
        # To captioning state
        if self.state == LobbyState.DRAWING:
            self.state = LobbyState.CAPTIONING
            for ctx in self.players:
                # Zero out the prompt for everyone, because we're going into captioning mode
                ctx.prompt = None
                # Append everyone's drawing to their held story
                self.stories[ctx.story_creator].append(StoryDrawing(ctx.name, ctx.drawing_data))
                # Move the creator of the story back
                ctx.story_creator = self.previous_player[ctx.story_creator]
                # Send out the previous person's drawing to be captioned
                messages.append(ctx.send({
                    "type": "captionPrompt",
                    "data": self.previous_player[ctx].drawing_data
                }))
        # To drawing state
        elif self.state == LobbyState.PROMPTING or self.state == LobbyState.CAPTIONING:
            self.state = LobbyState.DRAWING
            for ctx in self.players:
                # Zero out the drawing data, because we're going into drawing mode
                ctx.drawing_data = None
                # Append everyone's prompt to their held story
                self.stories[ctx.story_creator].append(StoryCaption(ctx.name, ctx.prompt))
                # Move the creator of the story back
                ctx.story_creator = self.previous_player[ctx.story_creator]
                # Send out the previous person's caption to be drawn
                messages.append(ctx.send({
                    "type": "drawPrompt",
                    "text": self.previous_player[ctx].prompt
                }))
        # Back to forming state
        elif self.state == LobbyState.REVIEWING:
            self.state = LobbyState.FORMING
            for ctx in self.players:
                message.append(ctx.send({
                    "type": "lobbyJoined",
                    "joinCode": self.join_code,
                    "roundTimer": self.round_timer,
                    "ownerName": self.owner.name
                    "players": [ctx.name for ctx in self.players],
                }))
        # Send any messages generated
        await asyncio.gather(*messages)

    def generate_player_order(self):
        player_order = list(self.players)
        random.shuffle(player_order)
        self.next_player = {ctx: player_order[(i+1) % len(player_order)] for i, ctx in enumerate(player_order)}
        self.previous_player = {v: k for k, v in self.next_player.items()}

    async def broadcast(self, message):
        await asyncio.gather(*[ctx.send(message) for ctx in self.players])

    def remove(self, ctx):
        # Remove this player
        self.players.discard(ctx)

        # If no one is left, delete the lobby
        if len(self.players) == 0:
            del Lobby.lobbies[self.join_code]

        # If this player was the owner, pick a new one
        elif ctx is self.owner:
            self.owner = random.choice(tuple(self.players))


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
    if hasattr(ctx, 'lobby') and ctx.lobby is not None:
        ctx.lobby.remove(ctx)

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


@register("nextReview")
async def on_review_next(ctx, message):
    """
    Move the review phase to the next caption / image.
    """
    if not ctx.lobby:
        raise GameError("No lobby")

    if ctx.lobby.state != LobbyState.REVIEWING:
        raise GameError("Invalid lobby state")

    if ctx is not ctx.lobby.owner:
        raise GameError("Not lobby owner")


    story = ctx.lobby.stories[ctx.lobby.stories_reviewed]

    # Move on to the next story when all elements are reviewed
    if ctx.lobby.elements_reviewed >= len(story):
        ctx.lobby.elements_reviewed = 0
        ctx.lobby.stories_reviewed += 1
        # If another nextReview is received after all stories have
        # been reviewed, return the the lobby.
        if ctx.lobby.stories_reviewed >= len(ctx.lobby.stories):
            await ctx.lobby.state_change()
            return
        story = ctx.lobby.stories[ctx.lobby.stories_reviewed]

    # Display the next element in this story
    element = story[ctx.lobby.elements_reviewed]
    ctx.lobby.elements_reviewed += 1
    await ctx.lobby.broadcast(element.to_dict())


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
        "roundTimer": lobby.round_timer,
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

    lobby = Lobby.lobbies.get(message['joinCode'])

    if lobby.state is not LobbyState.FORMING:
        raise GameError("Game has already started")

    lobby.players.add(ctx)
    ctx.lobby = lobby

    reply = {
        "type": "lobbyJoined",
        "joinCode": lobby.join_code,
        "roundTimer": lobby.round_timer,
        "ownerName": lobby.owner.name
        "players": [ctx.name for ctx in lobby.players],
    }

    return reply


@register("leaveLobby")
async def on_leave_lobby(ctx, message):
    """
    Leaves the user's current lobby.
    """
    if not ctx.lobby:
        return GameError("No lobby")

    ctx.lobby.remove(ctx)

    reply = {
        "type": "lobbyLeft",
    }

    return reply


@register("startGame")
async def on_start_game(ctx, message):
    if not ctx.lobby:
        raise GameError("No lobby")

    if ctx.lobby.state != LobbyState.FORMING:
        raise GameError("Invalid lobby state")

    if ctx is not ctx.lobby.owner:
        raise GameError("Not lobby owner")

    ctx.lobby.generate_player_order()
    ctx.lobby.state = LobbyState.PROMPTING
    ctx.lobby.stories = {ctx: [] for ctx in ctx.lobby.players}

    # Set each player's prompt to None
    for ctx in ctx.lobby.players:
        ctx.prompt = None
        ctx.story_creator = ctx

    await ctx.lobby.broadcast({
        "type": "startGame"
    })


@register("submitPrompt", [('prompt', str)])
async def on_submit_prompt(ctx, message):
    if not ctx.lobby:
        raise GameError("No lobby")
    if ctx.lobby.state != LobbyState.PROMPTING and ctx.lobby.state != LobbyState.CAPTIONING:
        raise GameError("Invalid lobby state")

    ctx.prompt = message['prompt']

    # Once all prompts are submitted, switch to drawing/reviewing mode
    if all(ctx.prompt for ctx in ctx.lobby.players):
        await ctx.lobby.state_change()


@register("submitDrawing", [('data', str)])
async def on_submit_drawing(ctx, message):
    if not ctx.lobby:
        raise GameError("No lobby")
    if ctx.lobby.state != LobbyState.PROMPTING:
        raise GameError("Invalid lobby state")

    ctx.drawing_data = message['data']

    # Once all drawings are submitted, switch to captioning/reviewing mode
    if all(ctx.drawing_data for ctx in ctx.lobby.players):
        await ctx.lobby.state_change()


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
