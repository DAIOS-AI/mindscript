import os
import requests
import json
from abc import abstractmethod
from mindscript.objects import MValue


TIMEOUT = 20


class Backend:
    # Must return a dict {"headers": dict, "json": dict}
    # to be submitted as an HTTP request.
    @abstractmethod
    def preprocess(self, prompt: str, output_grammar: str|None, output_schema: dict|None) -> dict:
        pass

    # Must return a string ready to be parsed by the interpreter.
    @abstractmethod
    def postprocess(self, jsonobj: dict) -> str:
        pass

    def consult(self, prompt: str, output_grammar: str|None, output_schema: dict|None):
        # print(f"Backend.consult: prompt = {prompt}")
        url = self.url
        data = self.preprocess(prompt, output_grammar, output_schema)
        try:
            with requests.post(url, timeout=TIMEOUT, **data) as response:
                res = response.json()
                # print(f"Backend.consult: res = {res}")
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
    def __init__(self, url=None, model=None):
        if "OPENAI_API_KEY" not in os.environ:
            raise ValueError("The environment variable 'OPENAI_API_KEY' is not set.")

        if url is not None:
            self.url = url
        else:
            self.url = "https://api.openai.com/v1/chat/completions" 

        if model is None:
            raise ValueError("The OpenAI backend requires a model name.")
        else:
            self.model = model

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.environ["OPENAI_API_KEY"]
        }
        self.temperature = 0.7

    def preprocess(self, prompt: str, output_grammar: str|None, output_schema: dict|None) -> dict:
        return {
            "headers": self.headers,
            "json": {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature
            }
        }

    def postprocess(self, res: dict):
        return res["choices"][0]["message"]["content"]


class Ollama(Backend):
    def __init__(self, url=None, model=None):
        if url is None:
            self.url = "http://localhost:11434/api/generate"
        else:
            self.url = url

        if model is None:
            raise ValueError("The Ollama backend requires a model name.")
        else:
            self.model = model

        self.headers = {"Content-Type": "application/json"}

    def preprocess(self, prompt: str, output_grammar: str|None, output_schema: dict|None) -> dict:
        return {
            "headers": self.headers,
            "json": {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "format": output_schema,
            }
        }

    def postprocess(self, res: dict):
        return res["response"]


class LlamaCPP(Backend):
    def __init__(self, url=None):
        if url is None:
            self.url = "http://localhost:8080/completion"
        else:
            self.url = url

        self.headers = {"Content-Type": "application/json"}
        self.max_tokens = 1000
        self.repeat_penalty = 1.5

    def preprocess(self, prompt: str, output_grammar: str|None, output_schema: dict|None) -> dict:
        return {
            "headers": self.headers,
            "json": {
                "prompt": prompt,
                "grammar": output_grammar,
                "n_predit": self.max_tokens,
                "repeat_penalty": self.repeat_penalty
            }
        }

    def postprocess(self, res: dict):
        return res["content"]
