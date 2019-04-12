# from __future__ import print_function
import logging
import sys


# _LOG_FORMAT = '%(asctime)s: %(message)s'
_log = logging.getLogger('pysp')
# _lhandler = logging.StreamHandler()
# _lhandler.setFormatter(logging.Formatter(_LOG_FORMAT))
# _log.addHandler(_lhandler)
# _log.propagate = 0


class Debug:
    DEBUG = False
    TAG_DEBUG = '[D] '
    TAG_ERROR = '[E] '
    TAG_INFO = '[I] '


class SDebug(Debug):
    def dprint(self, *args, **kwargs):
        if self.DEBUG:
            _log.debug(f"{self.TAG_DEBUG} {' '.join(args)}")
            # print(self.TAG_DEBUG, *args, file=sys.stderr, **kwargs)

    def eprint(self, *args, **kwargs):
        _log.error(f"{self.TAG_ERROR} {' '.join(args)}")
        # print(self.TAG_ERROR, *args, file=sys.stderr, **kwargs)

    def iprint(self, *args, **kwargs):
        _log.info(f"{self.TAG_INFO} {' '.join(args)}")
        # print(self.TAG_INFO, *args, file=sys.stderr, **kwargs)

class SCDebug(Debug):
    @classmethod
    def dprint(cls, *args, **kwargs):
        if cls.DEBUG:
            _log.debug(f"{cls.TAG_DEBUG} {' '.join(args)}")
            # print(cls.TAG_DEBUG, *args, file=sys.stderr, **kwargs)

    @classmethod
    def eprint(cls, *args, **kwargs):
        _log.error(f"{cls.TAG_ERROR} {' '.join(args)}")
        # print(cls.TAG_ERROR, *args, file=sys.stderr, **kwargs)

    @classmethod
    def iprint(cls, *args, **kwargs):
        _log.info(f"{cls.TAG_INFO} {' '.join(args)}")
        # print(cls.TAG_INFO, *args, file=sys.stderr, **kwargs)


class SError(Exception):
    pass
