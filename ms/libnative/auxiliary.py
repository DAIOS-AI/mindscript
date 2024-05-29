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

def import_code(code: str):
    ip = ms.startup.interpreter()
    startup_env = ip.env
    module_env = Environment(enclosing=startup_env)

    ip.env = module_env
    ip.eval(code)

    module_env.enclosing = None
    module = flattened_env(ip.env)
    module_env.enclosing = startup_env
    return module
