import os
import unittest

from pysp.string import KeyExpander

class KeyExpanderTest(unittest.TestCase):

    def _set_environ(self, kv):
        if kv:
            idx = kv.index('=')
            if idx > 0:
                os.environ[kv[:idx]] = kv[idx+1:]

    def test_environ_vars(self):
        testcase = (
            (True,  'ABC', 'ABC',  ''),
            (True,  'ABC', '$KEY', 'KEY=ABC'),
            (True,  'ABC.Value', '$KEY.Value', 'KEY=ABC'),
            (True,  'MyABC.Value', 'My$KEY.Value', 'KEY=ABC'),
            (True,  'ABC', '${KEY}', 'KEY=ABC'),
            (True,  'ABC.Value', '${KEY}.Value', 'KEY=ABC'),
            (True,  'MyABC.Value', 'My${KEY}.Value', 'KEY=ABC'),
            (True,  'My$NoKEY.Value', 'My$NoKEY.Value', ''),
            (True,  'My${NoKEY}.Value', 'My${NoKEY}.Value', ''),
            (True,  'MyABC$Value', 'My$KEY$Value', 'KEY=ABC'),
            (True,  'MyABC$Value', 'My$KEY$Value', 'KEY=ABC'),
            (False, 'MyABC_Value', 'My$KEY_Value', 'KEY=ABC'),
            (True,  'MyABC_Value', 'My${KEY}_Value', 'KEY=ABC'),
            (True,  'MyABC123', 'My${KEY}$Value', 'Value=123'),
        )
        for sch in '!@#%^&*()-=+{}[]|,./;:\'"`~<>?':
            testcase += (
                (True,  'MyABC{sch}value'.format(sch=sch),
                        'My${KEY}{sch}value'.format(KEY='KEY', sch=sch), ''),
                (True,  'MyABC{sch}value'.format(sch=sch),
                        'My$KEY{sch}value'.format(sch=sch), ''),
            )

        for case in testcase:
            rv, expected, string, keyvalue = case
            if keyvalue:
                self._set_environ(keyvalue)
            # print('@@', KeyExpander.environ_vars(string))
            assert rv == (expected == KeyExpander.environ_vars(string))
