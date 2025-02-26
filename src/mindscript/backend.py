import os
import requests
import json
from abc import abstractmethod
from mindscript.ast import Function
from mindscript.objects import MValue
from mindscript.oracle import MOracleFunction


TIMEOUT = 20


class Backend:
    # Must return a dict {"headers": dict, "json": dict}
    # to be submitted as an HTTP request.
    @abstractmethod
    def preprocess(self, oracle: MOracleFunction, prompt: str) -> dict:
        pass

    # Must return a string ready to be parsed by the interpreter.
    @abstractmethod
    def postprocess(self, jsonobj: dict) -> str:
        pass

    def consult(self, oracle: MOracleFunction, prompt: str):
        # print(f"Backend.consult: prompt = {prompt}")
        url = self.completionUrl
        data = self.preprocess(oracle, prompt)
        try:
            with requests.post(url, timeout=TIMEOUT, **data) as response:
                res = response.json()
                code = self.postprocess(res)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error: JSON decode failure of {response.text}")
        except requests.ConnectionError as e:
            raise ValueError(f"Error: Connection for {url}")
        except requests.Timeout as e:
            raise ValueError(f"Error: Timeout for {url}")
        except requests.HTTPError as e:
            raise ValueError(f"Error: HTTP error for {url}")
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error: Unknown request error for {url}")
        except KeyError as e:
            raise ValueError(f"Error: Unexpected reply: {res}")
        return code


class OpenAI(Backend):
    def __init__(self, url=None, model=None, apikey=None):
        if apikey is None and "OPENAI_API_KEY" not in os.environ:
            raise ValueError(
                "The environment variable 'OPENAI_API_KEY' is not set.")
        elif apikey is None and "OPENAI_API_KEY" in os.environ:
            apikey = os.environ["OPENAI_API_KEY"]

        if url is not None:
            self.url = url
        else:
            self.url = "https://api.openai.com"

        self.completionUrl = self.url + "/v1/chat/completions"

        if model is None:
            raise ValueError("The OpenAI backend requires a model name.")
        else:
            self.model = model

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.environ["OPENAI_API_KEY"]
        }

    def preprocess(self, oracle: MOracleFunction, prompt: str) -> dict:
        return {
            "headers": self.headers,
            "json": {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": oracle.output_name,
                        "schema": oracle.output_schema
                    },
                },
            }
        }

    def postprocess(self, res: dict):
        return res["choices"][0]["message"]["content"]


class Ollama(Backend):
    def __init__(self, url=None, model=None):
        if url is None:
            self.url = "http://localhost:11434"
        else:
            self.url = url

        self.completionUrl = self.url + "/api/generate"

        if model is None:
            raise ValueError("The Ollama backend requires a model name.")
        else:
            self.model = model

        self.headers = {"Content-Type": "application/json"}
        self.check_health()

    def check_health(self):
        url = self.url + "/"
        error_msg = f"Ollama backend error ({url}). Is the server online?"
        try:
            with requests.get(url, timeout=TIMEOUT) as response:
                if response.status_code != 200:
                    raise Exception(error_msg)
        except Exception:
            raise Exception(error_msg)
        return True

    def preprocess(self, oracle: MOracleFunction, prompt: str) -> dict:
        return {
            "headers": self.headers,
            "json": {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": oracle.output_schema,
            }
        }

    def postprocess(self, res: dict):
        return res["response"]


class LlamaCPP(Backend):
    def __init__(self, url=None):
        if url is None:
            self.url = "http://localhost:8080"
        else:
            self.url = url

        self.completionUrl = self.url + "/completion"

        self.headers = {"Content-Type": "application/json"}
        self.check_health()

    def check_health(self):
        url = self.url + "/health"
        error_msg = f"Llamacpp backend error ({self.url}). Is the server online?"
        try:
            with requests.get(url, timeout=TIMEOUT) as response:
                if response.status_code != 200:
                    raise Exception(error_msg)
        except Exception:
            raise Exception(error_msg)
        return True

    def preprocess(self, oracle: MOracleFunction, prompt: str) -> dict:
        return {
            "headers": self.headers,
            "json": {
                "prompt": prompt,
                "json_schema": oracle.output_schema,
            }
        }

    def postprocess(self, res: dict):
        return res["content"]
