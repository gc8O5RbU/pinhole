from loguru import logger

from enum import Enum
from dataclasses import dataclass, field
from collections import OrderedDict
from typing import List, Tuple, TYPE_CHECKING
from datetime import datetime


if TYPE_CHECKING:
    from pinhole.models.base import ChatModel


class Currency(Enum):
    USD = "USD"
    CNY = "CNY"


@dataclass
class Usage:
    ninput_tokens: int
    noutput_tokens: int
    time: datetime = field(default_factory=datetime.now)


@dataclass
class Statistics:
    model: 'ChatModel'
    usages: List[Usage] = field(default_factory=list)

    def get_token_count(self) -> Tuple[int, int]:
        ninput, noutput = 0, 0
        for usage in self.usages:
            ninput += usage.ninput_tokens
            noutput += usage.noutput_tokens

        return ninput, noutput

    def get_token_cost(self) -> Tuple[str, str]:
        ninput_tokens, noutput_tokens = self.get_token_count()
        input_price, output_price, currency = self.model.price()

        input_cost = ninput_tokens / 1E6 * input_price
        output_cost = noutput_tokens / 1E6 * output_price

        str_input_cost = f"{ninput_tokens} ({input_cost:.3f}{currency.value})"
        str_output_cost = f"{noutput_tokens} ({output_cost:.3f}{currency.value})"
        return str_input_cost, str_output_cost


@dataclass
class Profiler:
    stats: OrderedDict['ChatModel', Statistics] = field(default_factory=OrderedDict)

    def print_stats(self) -> None:
        logger.info("========== model profiling statistics ==========")
        for model, stats in self.stats.items():
            input_cost, output_cost = stats.get_token_cost()
            logger.info(f"{model.pretty_name()}: input-tokens {input_cost}, output-tokens {output_cost}")

    def print_detailed_stats(self) -> None:
        pass
