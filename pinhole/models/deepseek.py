from pinhole.models.openai import OpenaiCompatibleChatModel
from pinhole.models.base import Currency

from typing import Any, Dict, Tuple
from os import environ
from dataclasses import dataclass
from enum import Enum


@dataclass
class DeepSeekChatModel(OpenaiCompatibleChatModel):

    """ Models that are deployed at Deepseek.ai. You need to set the environment
    variable DEEPSEEK_API_KEY or manually provide the api key when initialize
    the model instance. """

    class Model(Enum):
        DEEPSEEK_CHAT = "deepseek-chat"
        DEEPSEEK_CODER = "deepseek-coder"

    api_key: str = environ.get("DEEPSEEK_API_KEY", "")
    model: Model = Model.DEEPSEEK_CHAT

    @property
    def api_address(self) -> str:
        return "https://api.deepseek.com/v1"

    @property
    def headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

    @property
    def model_name(self) -> str:
        return self.model.value

    def price(self) -> Tuple[float, float, Currency]:
        if self.model is self.Model.DEEPSEEK_CHAT:
            return 1, 2, Currency.CNY
        elif self.model is self.Model.DEEPSEEK_CODER:
            return 1, 2, Currency.CNY

        raise NotImplementedError(self.model)

    def detect_error(self, response: Any) -> Tuple[bool, str]:
        if 'code' in response:
            if response['code'] == 10003:
                return True, f"authentication error, please check API_KEY (current value is {self.api_key})"

        return False, ""

    def __hash__(self) -> int:
        return id(self)
