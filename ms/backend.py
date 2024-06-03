import os
import requests
import json
from abc import abstractmethod
from ms.objects import MValue


TIMEOUT = 20

class Backend:
    # Must return a dict {"headers": dict, "json": dict}
    # to be submitted as an HTTP request.
    @abstractmethod
    def preprocess(self, prompt: str, output_grammar: str):
        pass

    # Must return a string ready to be parsed by the interpreter.
    @abstractmethod
    def postprocess(self, jsonobj: dict):
        pass

    def consult(self, prompt: str, output_grammar: str):
        # print(f"Backend.consult: prompt = {prompt}")
        url = self.url
        data = self.preprocess(prompt, output_grammar)
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


class GPT3Turbo(Backend):
    def __init__(self):
        self.url = "https://api.openai.com/v1/chat/completions"
        if "OPENAI_API_KEY" not in os.environ:
            raise ValueError(
                "The environment variable 'OPENAI_API_KEY' is not set.")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.environ["OPENAI_API_KEY"]
        }
        self.temperature = 0.7

    def preprocess(self, prompt: str, output_grammar: str):
        return {
            "headers": self.headers,
            "json": {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature
            }
        }

    def postprocess(self, res: dict):
        return res["choices"][0]["message"]["content"]


class GPT4Turbo(Backend):
    def __init__(self):
        self.url = "https://api.openai.com/v1/chat/completions"
        if "OPENAI_API_KEY" not in os.environ:
            raise ValueError(
                "The environment variable 'OPENAI_API_KEY' is not set.")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.environ["OPENAI_API_KEY"]
        }
        self.temperature = 0.7

    def preprocess(self, prompt: str, output_grammar: str):
        return {
            "headers": self.headers,
            "json": {
                "model": "gpt-4-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature
            }
        }

    def postprocess(self, res: dict):
        return res["choices"][0]["message"]["content"]


class LlamaCPP(Backend):
    def __init__(self):
        self.url = "http://localhost:8080/completion"
        self.headers = {"Content-Type": "application/json"}
        self.max_tokens = 1000
        self.repeat_penalty = 1.5

    def preprocess(self, prompt: str, output_grammar: str):
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
