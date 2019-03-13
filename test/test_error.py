import io
import sys
import unittest

from pysp.serror import SDebug
from pysp.sbasic import stderr_redirector


if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")


class Test1Debug(SDebug):
    def __init__(self):
        pass


class Test2Debug(SDebug):
    def __init__(self):
        pass


class PyspDebugTest(unittest.TestCase, SDebug):
    # DEBUG = True

    def get_expected_msg(self, msg):
        return self.TAG_DEBUG + ' ' + msg + '\n'

    def test_pysp_debug1(self):
        # SDebug.DEBUG = False
        t1 = Test1Debug()
        t2 = Test2Debug()

        t1.DEBUG = True
        t1_dprint = 'T1 Print'
        t2_dprint = 'T2 Print'

        f = io.StringIO()
        with stderr_redirector(f):
            t1.dprint(t1_dprint)
            t2.dprint(t2_dprint)

        # SDebug.DEBUG = True
        stderr_msg = f.getvalue()
        self.dprint('Print: "{}"'.format(t1_dprint))
        self.dprint('Got  : "{}"'.format(stderr_msg))
        expected_msg = self.get_expected_msg(t1_dprint)
        print('@@@', expected_msg)
        self.assertTrue(expected_msg == stderr_msg)

        t1.DEBUG = False
        t2.DEBUG = True

        f = io.StringIO()
        with stderr_redirector(f):
            t1.dprint(t1_dprint)
            t2.dprint(t2_dprint)

        stderr_msg = f.getvalue()
        self.dprint('Print: "{}"'.format(t2_dprint))
        self.dprint('Got  : "{}"'.format(stderr_msg))
        expected_msg = self.get_expected_msg(t2_dprint)
        self.assertTrue(expected_msg == stderr_msg)

    def test_pysp_debug2(self):
        SDebug.DEBUG = True
        t1 = Test1Debug()
        t2 = Test2Debug()

        t1_dprint = 'T1 Print'
        t2_dprint = 'T2 Print'

        f = io.StringIO()
        with stderr_redirector(f):
            t1.dprint(t1_dprint)
            t2.dprint(t2_dprint)

        stderr_msg = f.getvalue()
        self.dprint('Print: "{}"'.format(t1_dprint))
        self.dprint('Got  : "{}"'.format(stderr_msg))
        expected_msg = self.get_expected_msg(t1_dprint)
        expected_msg += self.get_expected_msg(t2_dprint)
        self.assertTrue(expected_msg == stderr_msg)
        SDebug.DEBUG = False
