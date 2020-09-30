# -*- encoding: utf-8 -*-
import obj

Var  = lambda index:        obj.Data(0, [obj.Integer(index)])
App  = lambda fn, arg:      obj.Data(1, [fn, arg])
Abs  = lambda body:         obj.Data(2, [body])
Let  = lambda binds, body:  obj.Data(3, [obj.from_list(binds), body])
Enum = lambda index, arity: obj.Data(4, [obj.Integer(index), obj.Integer(arity)])
Case = lambda arg, alts:    obj.Data(5, [arg, obj.from_list(alts)])

class Reader(object):
    def __init__(self):
        self.state = 0
        self.variable = 0
        self.index = 0
        self.output = None
        self.aside = []

def output(reader, output):
    if reader.output is None:
        reader.output = output
    else:
        reader.output = App(reader.output, output)

def flush(reader, char):
    if reader.output is None:
        raise ReadError(char)
    else:
        repeat = True
        while repeat and len(reader.aside) > 0:
            arg = reader.output
            tag, reader.output, alts = reader.aside.pop()
            if tag == 0:                                    # group
                if char != ")":
                    raise ReadError(char)
                output(reader, arg)
                repeat = False
            elif tag == 1:                                  # let
                binds = [reader.output]
                while len(reader.aside) > 0 and reader.aside[len(reader.aside)-1][0] == 4:
                    _, bind, _ = reader.aside.pop()
                    binds.append(bind)
                binds.reverse()
                reader.output = Let(binds, arg)
            elif tag == 2:                                  # abs
                output(reader, Abs(arg))
            elif tag == 3:                                  # case
                if char != "}":
                    raise ReadError(char)
                reader.output = Case(reader.output, alts + [arg])
                repeat = False
            elif tag == 4:                                  # comma
                raise ReadError(char)
            else:
                raise ReadError(char)

def read_character(reader, char):
    if reader.state == 0:
        if char == " " or char == "\n" or char == "\t":
            reader.state = 0
        elif char.isdigit():
            reader.variable = to_digit(char)
            reader.state = 1
        elif ord(char) == 0xCE:
            reader.state = 2
        elif char == "(":
            reader.aside.append((0, reader.output, []))
            reader.output = None
            reader.state = 0
        elif char == ")":
            flush(reader, char)
            reader.state = 0
        elif char == "," and reader.output is not None:
            reader.aside.append((4, reader.output, []))
            reader.output = None
            reader.state = 0
        elif char == ":" and reader.output is not None:
            reader.aside.append((1, reader.output, []))
            reader.output = None
            reader.state = 0
        elif char == "{" and reader.output is not None:
            reader.aside.append((3, reader.output, []))
            reader.output = None
            reader.state = 0
        elif char == "}":
            flush(reader, char)
            reader.state = 0
        elif char == ";" and reader.output is not None:
            if len(reader.aside) > 0:
                tag, _, alts = reader.aside[len(reader.aside)-1]
                if tag != 3:
                    raise ReadError(char)
                alts.append(reader.output)
                reader.output = None
            else:
                raise ReadError(char)
        elif char == '#':
            reader.state = 20
        else:
            raise ReadError(char)
    elif reader.state == 1: # retrieving digits.
        if char.isdigit():
            reader.variable = reader.variable * 10 + to_digit(char)
            reader.state = 1
        elif char == "/":
            reader.state = 3
            reader.index = reader.variable
            reader.variable = 0
        else:
            reader.state = 0
            output(reader, Var(reader.variable))
            read_character(reader, char)
    elif reader.state == 2: # after 0xCE
        if ord(char) == 0xBB: # lambda read in.
            reader.aside.append((2, reader.output, []))
            reader.output = None
            reader.state = 0
        else:
            raise ReadError(char)
    elif reader.state == 3: # after N/
        if char.isdigit():
            reader.variable = reader.variable * 10 + to_digit(char)
            reader.state = 4
        else:
            raise ReadError(char)
    elif reader.state == 4: # after N/N
        if char.isdigit():
            reader.variable = reader.variable * 10 + to_digit(char)
            reader.state = 4
        else:
            reader.state = 0
            output(reader, Enum(reader.index, reader.variable))
            read_character(reader, char)
    elif reader.state == 20:
        if char == "\n":
            reader.state = 0
        else:
            reader.state = 20
    else:
        raise ReadError(char)

def read_done(reader):
    flush(reader, '\x00')
    if reader.output is None:
        raise ReadError('\x00')
    else:
        return reader.output

class ReadError(Exception):
    def __init__(self, char):
        self.char = char

    def rep(self):
        return "When trying to read char 0x%x" % (ord(self.char))

def to_digit(char):
    return ord(char) - ord('0')
