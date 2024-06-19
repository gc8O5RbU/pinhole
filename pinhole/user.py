from pydantic.dataclasses import dataclass, Field
from pydantic.root_model import RootModel
from typing import Any


@dataclass
class AuthRequest:
    email: str
    password: str


@dataclass
class User:
    email: str
    nickname: str
    password: str


@dataclass
class UserRef:
    id: int
    email: str
    nickname: str

    @classmethod
    def from_json(cls, data: Any) -> 'UserRef':
        return RootModel[UserRef].model_validate(data).root
