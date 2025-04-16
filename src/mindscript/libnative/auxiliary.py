import mindscript.backend
from mindscript.runtime import Environment
import mindscript.builtins

def flattened_env(env: Environment):
    fenv = dict()
    while env is not None:
        for key, val in env.vars.items():
            if key not in fenv:
                fenv[key] = val
        env = env.enclosing
    return fenv

def import_code(code: str, backend: mindscript.backend.Backend, buffer: str = None):
    ip = mindscript.builtins.interpreter(backend=backend)
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
