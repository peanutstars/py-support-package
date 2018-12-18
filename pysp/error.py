from __future__ import print_function
import sys
# from functools import partial
#
# _print = partial(print, file=sys.stdout)



class PyspDebug:
    DEBUG = False
    TAG_DEBUG = '[D] '
    TAG_ERROR = '[E] '

    # @classmethod
    def dprint(self, *args, **kwargs):
        if self.DEBUG:
            print(self.TAG_DEBUG, *args, file=sys.stderr, **kwargs)

    # @classmethod
    def eprint(self, *args, **kwargs):
        print(self.TAG_ERROR, *args, file=sys.stderr, **kwargs)

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
        # return ''

class PyspError(Exception):
    pass
