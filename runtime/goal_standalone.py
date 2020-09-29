import os
import obj
import term
import evaluator

def entry_point(argv):
    exit_status = 0
    try:
        filename = argv[1]
    except IndexError:
        load_fd(0)
    else:
        fd = os.open(filename, os.O_RDONLY, 0777)
        load_fd(fd)
        os.close(fd)
    return exit_status

def load_fd(fd):
    reader = term.Reader()
    try:
        while True:
            text = os.read(fd, 4096)
            if len(text) == 0:
                break;
            for char in text:
                term.read_character(reader, char)
        program = term.read_done(reader)
    except term.ReadError as e:
        os.write(1, "ReadError: %s\n" % (e.rep()))
    else:
        thunk = evaluator.activate([], program)
        result = thunk.enter([])
        if isinstance(result, obj.Integer):
            os.write(1, "Returned an integer %d\n" % result.number)
        elif isinstance(result, obj.Data):
            os.write(1, "Returned a tag %d\n" % result.tag)
        else:
            os.write(1, "Returned non-integer non-tag.\n")

def target(driver, args):
    driver.exe_name = "lijp"
    return entry_point, None

if __name__=="__main__":
    from rpython.config.translationoption import get_combined_translation_config
    import sys
    config = get_combined_translation_config(translating=True)
    sys.exit(entry_point(config)(sys.argv))
