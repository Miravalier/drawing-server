import json
import random
import string
from dataclasses import dataclass, fields


def json_dataclass(cls):
    """
    Annotation wrapper for dataclass that adds json
    properties.
    """
    # Call dataclass annotation
    cls = dataclass(cls)
    field_names = tuple(field.name for field in fields(cls))

    # Add json properties
    def data_property(self):
        return {name: getattr(self, name) for name in field_names}

    def json_property(self):
        return json.dumps(self.data)

    cls.data = property(data_property)
    cls.json = property(json_property)

    # Return updated class
    return cls


@json_dataclass
class Player:
    id: str
    name: str
    ready: bool = False


class Lobby:
    instances = {}

    def __init__(self, owner, public, players=None, join_code=None):
        if players is None:
            players = {}
        if join_code is None:
            join_code = "".join(random.choice(string.ascii_letters) for _ in range(8))

        self.owner = owner
        self.public = public
        self.players = players
        self.join_code = join_code

    @property
    def data(self):
        return {
            "owner": self.owner.data,
            "public": self.public,
            "players": [player.data for player in self.players.values()]
        }

    @property
    def json(self):
        return json.dumps(self.data)

    @property
    def players_json(self):
        return json.dumps([player.data for player in self.players.values()])

    @classmethod
    def create(cls, owner, public):
        lobby = cls(owner, public, {owner.id: owner})
        cls.instances[owner.id] = lobby
        return lobby
