import obj

class Prog(obj.Object):
    def __init__(self, env, body):
        self.env = env
        self.body = body
    
    def enter(self, args):
        return evaluate(self.env, self.body, args)

class Thunk(obj.Object):
    def __init__(self, ref):
        self.ref = ref

    def enter(self, args):
        if self.ref is None:
            raise obj.RuntimeTypeError() # Blackholed reference
        ref, self.ref = self.ref, None
        self.ref = ref.enter([])
        return self.ref.enter(args)

class PAP(obj.Object):
    def __init__(self, fun, args):
        self.fun = fun
        self.args = args

    def enter(self, args):
        args.extend(self.args)
        return self.fun.enter(args)

# Var  = lambda index:        obj.Data(0, [obj.Integer(index)])
# App  = lambda fn, arg:      obj.Data(1, [fn, arg])
# Abs  = lambda body:         obj.Data(2, [body])
# Let  = lambda binds, body:  obj.Data(3, [obj.from_list(binds), body])
# Enum = lambda index, arity: obj.Data(4, [obj.Integer(index), obj.Integer(arity)])
# Case = lambda arg, alts:    obj.Data(5, [arg, obj.from_list(alts)])

def lookup(env, index):
    if index < len(env):
        return env[len(env) - index - 1]
    else:
        raise obj.RuntimeTypeError()

def activate(env, expr):
    data = obj.to_data(expr)
    if data.tag == 0:   # Var
        return lookup(env, obj.to_integer(data.args[0]))
    elif data.tag == 1: # App
        if examine(data):
            return evaluate(env, data, [])
        else:
            return Thunk(Prog(env, data))
    elif data.tag == 2: # Abs
        return Prog(env, data)
    elif data.tag == 3: # Let
        binds = obj.to_list(data.args[0])
        bound_env = []
        for bind in binds:
            bound_env.append(activate(env, bind))
        env = env + bound_env
        return activate(env, data.args[1])
    elif data.tag == 4: # Enum
        return evaluate(env, data, [])
    elif data.tag == 5: # Case
        return Prog(env, data)
    else:
        raise obj.RuntimeTypeError()

def examine(data):
    if data.tag == 0: # Var
        return False
    elif data.tag == 1: # App
        return examine(data.args[0])
    elif data.tag == 2: # Abs
        return False
    elif data.tag == 3: # Let
        return examine(data.args[1])
    elif data.tag == 4: # Enum
        return True
    elif data.tag == 5: # Case
        return False
    else:
        raise obj.RuntimeTypeError()

def evaluate(env, expr, args):
    data = obj.to_data(expr)
    if data.tag == 0: # Var
        return lookup(env, obj.to_integer(data.args[0])).enter(args)
    elif data.tag == 1: # App
        fn = data.args[0]
        arg = data.args[1]
        args.append(activate(env, arg))
        return evaluate(env, fn, args)
    elif data.tag == 2: # Abs
        try:
            env = env + [args.pop()]
        except IndexError:
            return PAP(Prog(env, data), args)
        return evaluate(env, data.args[0], args)
    elif data.tag == 3: # Let
        binds = obj.to_list(data.args[0])
        bound_env = []
        for bind in binds:
            bound_env.append(activate(env, bind))
        env = env + bound_env
        return evaluate(env, data.args[1], args)
    elif data.tag == 4: # Enum
        index = obj.to_integer(data.args[0])
        arity = obj.to_integer(data.args[1])
        if len(args) < arity:
            return PAP(Prog([], data), args)
        elif len(args) == arity:
            args.reverse()
            return obj.Data(index, args)
        else:
            raise obj.RuntimeTypeError()
    elif data.tag == 5: # Case
        seq  = obj.to_list(data.args[1])
        case = obj.to_data(activate(env, data.args[0]))
        if case.tag < len(seq):
            for arg in reversed(case.args):
                args.append(arg)
            return evaluate(env, seq[case.tag], args)
        else:
            raise obj.RuntimeTypeError()
    else:
        raise obj.RuntimeTypeError()
