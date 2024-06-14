from pinhole.models.base import ChatModel, ChatContext, Currency

from typing import Any, Dict, Tuple, List
from os import environ
from dataclasses import dataclass
from enum import Enum
from loguru import logger

from zhipuai import ZhipuAI  # type: ignore


@dataclass
class GLMChatModel(ChatModel):

    """ Models that are deployed at Deepseek.ai. You need to set the environment
    variable DEEPSEEK_API_KEY or manually provide the api key when initialize
    the model instance. """

    class Model(Enum):
        GLM4 = "glm-4"
        GLM4_AIR = "glm-4-air"
        GLM4_FLASH = "glm-4-flash"

    api_key: str = environ.get("GLM_API_KEY", "")
    model: Model = Model.GLM4_FLASH

    @property
    def api_address(self) -> str:
        return "https://open.bigmodel.cn/api/paas/v4"

    @property
    def client(self) -> ZhipuAI:
        if not hasattr(self, "_client"):
            client = ZhipuAI(api_key=self.api_key)
            setattr(self, "_client", client)
            return client
        else:
            return getattr(self, "_client")

    def validate(self) -> bool:
        if self.api_key == "":
            logger.error(f"no api-key configured for glm models, please set the environment variable GLM_API_KEY")
            return False

        test_messages = [{"role": "user", "content": "test"}]
        _ = self.client.chat.completions.create(model=self.model.value, messages=test_messages, max_tokens=2)
        return True

    def pretty_name(self) -> str:
        return self.model.value

    @property
    def model_name(self) -> str:
        return self.model.value

    def price(self) -> Tuple[float, float, Currency]:
        if self.model is self.Model.GLM4:
            return 100, 100, Currency.CNY
        elif self.model is self.Model.GLM4_AIR:
            return 1, 1, Currency.CNY
        elif self.model is self.Model.GLM4_FLASH:
            return 0.1, 0.1, Currency.CNY

        raise NotImplementedError(self.model)

    def chat(self, context: ChatContext) -> str:
        messages: List[Dict[str, str]] = []
        messages.append({"role": "system", "content": context.system_prompt})

        for r, msg in context.history:
            messages.append({"role": r.value, "content": msg})

        finish_reason = "not_finished"
        while finish_reason != "stop":
            completion = self.client.chat.completions.create(
                model=self.model.value,
                messages=messages,
                tools=[]
            )

            prompt_tokens = completion.usage.prompt_tokens
            completion_tokens = completion.usage.completion_tokens
            self.notify_usage(prompt_tokens, completion_tokens)

            choice = completion.choices[0]
            message = choice.message

            finish_reason = choice.finish_reason

            #############################################################
            # interprete tool calls if needed
            #############################################################

            messages.append(message)
            content = message.content

        return content

    def __hash__(self) -> int:
        return id(self)
