from pinhole.models.base import ChatContext, ChatModel, Currency

from loguru import logger
from typing import Any, Dict, List, Tuple
from dataclasses import dataclass
from time import sleep
from enum import Enum
from os import environ

import json
import requests


@dataclass
class OpenaiCompatibleChatModel(ChatModel):

    @property
    def api_address(self) -> str:
        raise NotImplementedError

    @property
    def model_name(self) -> str:
        raise NotImplementedError

    def pretty_name(self) -> str:
        return self.model_name

    @property
    def headers(self) -> Dict[str, str]:
        return dict()

    def detect_error(self, response: Any) -> Tuple[bool, str]:
        return False, ""

    def validate(self) -> bool:
        headers = {"Content-Type": "application/json"}
        headers.update(self.headers)
        resp = requests.get(
            f"{self.api_address}/models",
            headers=headers
        )

        if resp.status_code != 200:
            logger.info(f"http status code {resp.status_code}: {resp.text}")
            logger.critical(f"model validation failed: cannot get model list")
            return False

        for obj_info in resp.json()["data"]:
            if obj_info.get("object", "") == "model":
                if obj_info.get("id", "") == self.model_name:
                    return True

        logger.critical(f"cannot find model {self.model_name} on the API server")
        return False

    def __chat_post(self, headers: Dict[str, str], body: object) -> requests.Response:
        while True:
            resp = requests.post(
                f"{self.api_address}/chat/completions",
                headers=headers,
                json=body
            )

            if resp.status_code == 200:
                return resp
            elif resp.status_code == 429:
                logger.warning(f"rate limiatation reached, retry after 10 seconds")
                sleep(10)
            elif resp.status_code == 400:
                raise Exception(f"request failed: {resp.text}")
            else:
                logger.warning(resp.text)
                raise Exception(f"request failed: {resp.status_code}")

    def chat(self, context: ChatContext) -> str:
        messages: List[Dict[str, str]] = []
        messages.append({"role": "system", "content": context.system_prompt})

        for r, msg in context.history:
            messages.append({"role": r.value, "content": msg})

        request_body = {
            "model": self.model_name,
            "messages": messages,
            "temperature": 0
        }

        headers = {"Content-Type": "application/json"}
        headers.update(self.headers)

        finish_reason = "not_finished"
        while finish_reason != "stop":

            resp = self.__chat_post(headers, request_body)

            resp_json = resp.json()
            has_error, reason = self.detect_error(resp_json)
            if has_error:
                raise Exception(reason)

            prompt_tokens = resp_json["usage"]["prompt_tokens"]
            completion_tokens = resp_json["usage"]["completion_tokens"]
            self.notify_usage(prompt_tokens, completion_tokens)

            choice = resp_json["choices"][0]
            message = choice["message"]
            finish_reason = choice['finish_reason']

            messages.append(message)
            content = message["content"]

        return content


@dataclass
class OpenaiChatModel(OpenaiCompatibleChatModel):

    class Model(Enum):
        GPT_4 = "gpt-4"
        GPT_4O = "gpt-4o"
        GPT_35_TURBO = "gpt-3.5-turbo"

    api_key: str = environ.get("OPENAI_API_KEY", "")
    model: Model = Model.GPT_35_TURBO

    @property
    def api_address(self) -> str:
        return "https://api.openai.com/v1"

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    @property
    def model_name(self) -> str:
        return self.model.value

    @property
    def support_tool_use(self) -> bool:
        return True

    def price(self) -> Tuple[float, float, Currency]:
        if self.model is self.Model.GPT_4:
            return (10, 30, Currency.USD)
        if self.model is self.Model.GPT_4O:
            return (5, 15, Currency.USD)
        if self.model is self.Model.GPT_35_TURBO:
            return (0.5, 1.5, Currency.USD)

    def __hash__(self) -> int:
        return id(self)
