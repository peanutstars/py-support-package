import os
import unittest

from pysp.basic import StrExpand, FileOp
from pysp.conf import Config
from pysp.error import PyspDebug


class StrExpandTest(PyspDebug, FileOp, unittest.TestCase):

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
            # print('@@', StrExpand.environ_vars(string))
            assert rv == (expected == StrExpand.environ_vars(string))

    def test_config_vars(self):
        yml_string = '''
vehicle:
    sedan:
        fuel: [disel, gasoline]
        wheels: 4
    suv:
        fuel: [disel, gasoline]
        wheels: 4

text1: Sedan has @vehicle.sedan.wheels tires.
text2: Engine is two types - @{vehicle.suv.fuel}.
'''
        vehicle_file = '/tmp/test/vehicle.yml'
        self.str_to_file(vehicle_file, yml_string)
        cfg = Config(vehicle_file)
        # self.DEBUG = True
        cvt_text1 = StrExpand.config_vars(cfg, cfg.get_value('text1'))
        cvt_text2 = StrExpand.config_vars(cfg, cfg.get_value('text2'))
        self.assertTrue(cvt_text1 == 'Sedan has 4 tires.')
        self.assertTrue(cvt_text2 == 'Engine is two types - disel,gasoline.')
