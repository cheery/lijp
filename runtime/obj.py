class Object(object):
    def enter(self, args):
        if len(args) == 0:
            return self
        else:
            raise RuntimeTypeError()

class RuntimeTypeError(Exception):
    pass

class Integer(Object):
    def __init__(self, number):
        self.number = number

class Data(Object):
    def __init__(self, tag, args):
        self.tag = tag
        self.args = args

def from_list(lst):
    head = Data(0, [])
    for arg in reversed(lst):
        head = Data(1, [arg, head])
    return head

def to_integer(value):
    result = value.enter([])
    if isinstance(result, Integer):
        return result.number
    else:
        raise RuntimeTypeError()

def to_data(value):
    result = value.enter([])
    if isinstance(result, Data):
        return result
    else:
        raise RuntimeTypeError()

def to_list(value):
    data = to_data(value)
    out = []
    while data.tag == 1 and len(data.args) == 2:
        out.append(data.args[0])
        data = to_data(data.args[1])
    if data.tag == 0 and len(data.args) == 0:
        return out
    else:
        raise RuntimeTypeError()
