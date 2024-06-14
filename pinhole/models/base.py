from pinhole.models.profiler import Currency, Profiler, Statistics, Usage

from loguru import logger

from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from math import inf
from enum import Enum


class Role(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class ChatContext:
    model: 'ChatModel'
    task_identifier: str = "default"
    system_prompt: str = "You are a useful assistant."
    history: List[Tuple[Role, str]] = field(default_factory=list)

    def fork(self) -> 'ChatContext':
        return ChatContext(
            model=self.model,
            task_identifier=self.task_identifier,
            system_prompt=self.system_prompt,
            history=list(self.history)
        )

    def chat(self, message: str) -> str:
        self.history.append((Role.USER, message))
        response = self.model.chat(self)
        self.history.append((Role.ASSISTANT, response))
        return response

    def summary(self) -> str:
        s = f"Model: {self.model.pretty_name()}\n\n"
        s += "====== SYSTEM ======\n"
        s += self.system_prompt + "\n"
        for role, msg in self.history:
            s += f"====== {role.value} ======\n"
            s += msg + "\n"

        return s

    def summary_json(self) -> object:
        return {
            "model": self.model.pretty_name(),
            "system_prompt": self.system_prompt,
            "history": [
                {"role": role.value, "content": msg}
                for role, msg in self.history
            ]
        }

    def clear(self) -> None:
        self.history.clear()


@dataclass
class ChatModel:

    profiler: Optional[Profiler] = field(default=None, init=False)

    @property
    def support_system_prompt(self) -> bool:
        return True

    @property
    def support_tool_use(self) -> bool:
        return False

    def pretty_name(self) -> str:
        raise NotImplementedError

    def chat(self, context: ChatContext) -> str:
        raise NotImplementedError

    def fork(self) -> 'ChatModel':
        raise NotImplementedError

    def price(self) -> Tuple[float, float, Currency]:
        """ Returns (price/million input tokens, price/million output tokens, currency unit) """
        return (inf, inf, Currency.CNY)

    def notify_usage(self, n_input_tokens: int, n_output_tokens: int) -> None:
        if self.profiler is None:
            return

        if self not in self.profiler.stats:
            self.profiler.stats[self] = Statistics(self)

        stats = self.profiler.stats[self]
        stats.usages.append(Usage(n_input_tokens, n_output_tokens))

    def validate(self) -> bool:
        """ Validate whether the chat model is properly configured. """
        return True
