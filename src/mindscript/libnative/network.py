from typing import List, Any
from copy import deepcopy
import requests
import mindscript 
from mindscript.objects import MNativeFunction, MValue, MObject
from mindscript.runtime import Interpreter
import datetime

# Basic HTTP operations: http_get, http_post, http_put, http_delete
# Handling responses and headers: get_headers, get_body
# Sockets:
# TCP/UDP socket operations: create_socket, bind, listen, connect, send, receive, close

#     method: "POST", // *GET, POST, PUT, DELETE, etc.
#     mode: "cors", // no-cors, *cors, same-origin
#     cache: "no-cache", // *default, no-cache, reload, force-cache, only-if-cached
#     credentials: "same-origin", // include, *same-origin, omit
#     headers: {
#       "Content-Type": "application/json",
#       // 'Content-Type': 'application/x-www-form-urlencoded',
#     },
#     redirect: "follow", // manual, *follow, error
#     referrerPolicy: "no-referrer", 
#     // no-referrer, *no-referrer-when-downgrade, origin, origin-when-cross-origin, 
#     // same-origin, strict-origin, strict-origin-when-cross-origin, unsafe-url
#     body: JSON.stringify(data)

HTTPParams = """let HTTPParams = type {
    mode: Str?,
    cache: Str?,
    credentials: Str?,
    headers: {}?,
    redirect: Str?,
    referrerPolicy: Str?,
    body: {} 
}"""

class HTTP(MNativeFunction):
    def __init__(self, ip: Interpreter):
        super().__init__(ip, "fun(params: HTTPParams?, method: Str?, url: Str) -> {}")
        self.annotation = "Makes an HTTP request."

    def func(self, args: List[MObject]):
        wparams, method, url = args

        params = mindscript.unwrap(wparams)
        if params is None:
            params = {}
        if method.value is None:
            method = MValue("GET", None)
        try:
            with requests.request(method.value, url.value, **params) as response:
                result = {
                    "statusCode": response.status_code,
                    "headers": dict( response.headers.items() ),
                    "cookies": requests.utils.dict_from_cookiejar(response.cookies),
                    "encoding": response.encoding,
                    "elapsed_ms": response.elapsed / datetime.timedelta(milliseconds=1),
                    "reason": response.reason,
                    "is_permanent_redirect": response.is_permanent_redirect,
                    "is_redirect": response.is_redirect,
                    "text": response.text,
                    "url": response.url
                }
                if "Content-Type" in response.headers and response.headers["Content-Type"] == "application/json":
                    result["json"] = response.json()
                return mindscript.wrap(result)
        except requests.JSONDecodeError as e:
            result = {
                "error": "JSON decode error",
                "detail": str(e)
            }
        except requests.ConnectionError as e:
            result = {
                "error": "Connection error",
                "detail": str(e)
            }
            return mindscript.wrap(result)
        except requests.Timeout as e:
            result = {
                "error": "Timeout error",
                "detail": str(e)
            }
            return mindscript.wrap(result)
        except requests.HTTPError as e:
            result = {
                "error": "HTTP error",
                "detail": str(e)
            }
            return mindscript.wrap(result)
        except requests.exceptions.RequestException as e:
            result = {
                "error": "Unknown request error",
                "detail": str(e)
            }
            return mindscript.wrap(result)


