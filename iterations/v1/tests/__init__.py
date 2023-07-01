import inspect

# TODO(pbz): Make this a fixture instead?
def reporter(**kwargs):
    message = ' ('
    for name, value in kwargs.items():
        message += f'{name}=`{value}`,'
    message += ')'
    def closure(info=''):
        nonlocal message
        return info + message
    return closure

class Pass(Exception):
    pass
