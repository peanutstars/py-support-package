# -*- coding: utf-8 -*-

import os
import shutil
import unittest

from pysp.yaml import YAML
from pysp.error import PyspDebug


main_yml = '''
main:
    cmd: main-command
    sublevel: !include sub_l1.yml
    tag: main
'''.strip()

sub_l1_yml = '''
cmd: sub-command
sublevel: !include sub_l2.yml
tag: sub level 1
'''.strip()

sub_l2_yml = '''
cmd: sub-command
sublevel: null
tag: sub level 2
'''.strip()

expected_mark_yml = '''
__include__:
    fullpath: /tmp/yaml/main.yml
    value: null
main:
    cmd: main-command
    sublevel:
        __include__:
            fullpath: /tmp/yaml/sub_l1.yml
            value: sub_l1.yml
        cmd: sub-command
        sublevel:
            __include__:
                fullpath: /tmp/yaml/sub_l2.yml
                value: sub_l2.yml
            cmd: sub-command
            sublevel: null
            tag: sub level 2
        tag: sub level 1
    tag: main
'''.strip()

expected_yml = '''
main:
    cmd: main-command
    sublevel:
        cmd: sub-command
        sublevel:
            cmd: sub-command
            sublevel: null
            tag: sub level 2
        tag: sub level 1
    tag: main
'''.strip()


yml_files = [main_yml, sub_l1_yml, sub_l2_yml]

def get_var_name(var, dir=locals()):
    return [key for key, val in dir.items() if id(val) == id(var)]



class YamlTest(unittest.TestCase, PyspDebug):
    # DEBUG = True
    folder = '/tmp/yaml/'

    def convert_filename(self, var):
        fname = get_var_name(var)[0].split('_')
        return self.folder+'_'.join(fname[:-1])+'.'+fname[-1]

    def load_test(self):
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

        for item in yml_files:
            fpath = self.convert_filename(item)
            self.str_to_file(fpath, item)
        yfile = self.convert_filename(yml_files[0])
        self.ymlo = YAML.load(yfile)
        loaded_yml = YAML.dump(self.ymlo, pretty=True).strip()
        self.dprint(loaded_yml)
        self.assertTrue(loaded_yml ==  expected_mark_yml)

    def store_test(self):
        shutil.rmtree(self.folder)
        os.makedirs(self.folder)
        YAML.store(self.ymlo)

        for item in yml_files:
            fpath = self.convert_filename(item)
            data = self.file_to_str(fpath).strip()
            self.dprint('Load: {}'.format(fpath))
            self.assertTrue(data == item)


    def test_yaml(self):
        self.load_test()
        self.store_test()
