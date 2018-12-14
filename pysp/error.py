from __future__ import print_function
import sys
from functools import partial

_print = partial(print, file=sys.stderr)


class PyspDebug:
    DEBUG = False
    TAG_DEBUG = '[D] '
    TAG_ERROR = '[E] '

    @classmethod
    def dprint(cls, *args, **kwargs):
        if cls.DEBUG:
            _print(cls.TAG_DEBUG, *args, **kwargs)

    @classmethod
    def eprint(cls, *args, **kwargs):
        _print(cls.TAG_ERROR, *args, **kwargs)

    @classmethod
    def str_to_file(cls, fpath, data):
        with open(fpath, 'w') as fd:
            fd.write(data)

    @classmethod
    def file_to_str(cls, fpath):
        with open(fpath, 'r') as fd:
            return fd.read()

    @classmethod
    def file_to_readline(cls, fpath):
        with open(fpath, 'r') as fd:
            for line in fd:
                yield line
        return ''

class PyspError(Exception):
    pass
