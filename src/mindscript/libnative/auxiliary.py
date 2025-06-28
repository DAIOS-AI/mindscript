import mindscript.backend
from mindscript.runtime import Environment
import mindscript.builtins

def flattened_env(env: Environment):
    fenv = dict()
    while not env.startup:
        for key, val in env.vars.items():
            if key not in fenv:
                fenv[key] = val
        env = env.enclosing
    return fenv

def import_code(
        ip: 'Interpreter', code: str, # type: ignore
        backend: mindscript.backend.Backend, buffer: str = None):
    
    startup_env = ip.env
    while not startup_env.startup:
        startup_env = startup_env.enclosing
    module_env = Environment(enclosing=startup_env)

    cur_env = ip.env               # Save environment.
    cur_buffer = ip.buffer         # Save buffer.
    ip.env = module_env
    ip.eval(code, buffer)
    ip.set_buffer(cur_buffer)      # Restore buffer.

    module = flattened_env(ip.env)
    ip.env = cur_env # Restore environment.
    return module
