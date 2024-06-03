import ms.backend
from ms.interpreter import Environment
import ms.startup

def flattened_env(env: Environment):
    fenv = dict()
    while env is not None:
        for key, val in env.vars.items():
            if key not in fenv:
                fenv[key] = val
        env = env.enclosing
    return fenv

def import_code(code: str, backend: ms.backend.Backend, buffer: str = None):
    ip = ms.startup.interpreter(backend=backend)
    startup_env = ip.env
    module_env = Environment(enclosing=startup_env)

    ip.env = module_env
    buffer = ip.buffer
    ip.eval(code, buffer)
    ip.set_buffer(buffer)

    module_env.enclosing = None
    module = flattened_env(ip.env)
    module_env.enclosing = startup_env
    return module
