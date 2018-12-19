from __future__ import print_function
import sys
# from functools import partial
#
# _print = partial(print, file=sys.stdout)



class PyspDebug:
    DEBUG = False
    TAG_DEBUG = '[D] '
    TAG_ERROR = '[E] '
    TAG_INFO  = '[I] '

    def dprint(self, *args, **kwargs):
        if self.DEBUG:
            print(self.TAG_DEBUG, *args, file=sys.stderr, **kwargs)

    def eprint(self, *args, **kwargs):
        print(self.TAG_ERROR, *args, file=sys.stderr, **kwargs)

    def iprint(self, *args, **kwargs):
        print(self.TAG_INFO, *args, file=sys.stderr, **kwargs)


class PyspError(Exception):
    pass
