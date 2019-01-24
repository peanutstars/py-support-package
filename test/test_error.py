import io
import os
import sys
import unittest

from pysp.error import PyspDebug
from pysp.basic import stderr_redirector



if sys.version_info[0] < 3:
    raise Exception("Must be using Python 3")



class Test1Debug(PyspDebug):

    def __init__(self):
        pass

class Test2Debug(PyspDebug):

    def __init__(self):
        pass



class PyspDebugTest(unittest.TestCase, PyspDebug):
    # DEBUG = True

    def get_expected_msg(self, msg):
        return self.TAG_DEBUG + ' ' + msg + '\n'

    def test_pyspdebug(self):
        t1 = Test1Debug()
        t2 = Test2Debug()

        t1.DEBUG = True
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


    def test_pyspdebug(self):
        PyspDebug.DEBUG = True
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
        expected_msg = self.get_expected_msg(t1_dprint) + \
                       self.get_expected_msg(t2_dprint)
        self.assertTrue(expected_msg == stderr_msg)
        PyspDebug.DEBUG = False
