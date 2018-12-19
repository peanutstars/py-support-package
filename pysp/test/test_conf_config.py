
import os
import shutil
import unittest

from pysp.basic import FileOp
from pysp.error import PyspDebug
from pysp.conf import Config

class Expected:
    default_vehicle = '''
car:
    sedan:
        SM6:
            transmission: cvt
    suv:
        QM6:
            transmission: cvt
'''.strip()

    user_vehicle = '''
car:
    suv:
        QM6:
            color: cloud-perl
            transmission: CVT
'''.strip()

    overlay_user_vehicle = '''
car:
    sedan:
        SM6:
            transmission: cvt
    suv:
        QM6:
            color: cloud-perl
            transmission: CVT
'''.strip()


class FolderConfig:
    root = '''
car:
    sedan: !include folder/sedan
    suv: !include folder/suv

'''.strip()

    car_sedan = '''
SM6:
    transmission: cvt
'''.strip()

    car_suv = '''
QM6:
    transmission: cvt
'''.strip()


class ConfigTest(unittest.TestCase, PyspDebug, FileOp):
    # DEBUG = True
    def_folder = '/tmp/yaml/default/'
    user_folder = '/tmp/yaml/user/'

    def config_create_default(self):
        cfg = Config()
        cfg.set_value('car.suv.QM6.transmission', 'cvt')
        cfg.set_value('car.sedan.SM6.transmission', 'cvt')
        cfgfile = self.def_folder+'vehicle'
        cfg.store(cfgfile)
        load_vehicle = self.file_to_str(cfgfile).strip()
        self.assertTrue(Expected.default_vehicle == load_vehicle)

    def config_create_user(self):
        cfg = Config()
        cfg.set_value('car.suv.QM6.transmission', 'CVT')
        cfg.set_value('car.suv.QM6.color', 'cloud-perl')
        cfgfile = self.user_folder+'vehicle'
        cfg.store(cfgfile)
        load_vehicle = self.file_to_str(cfgfile).strip()
        self.assertTrue(Expected.user_vehicle == load_vehicle)

    def config_merge(self):
        cfg = Config(self.def_folder+'vehicle')
        cfg.overlay(self.user_folder+'vehicle')
        cfg.store()
        cfgfile = self.user_folder+'vehicle'
        load_vehicle = self.file_to_str(cfgfile).strip()
        self.assertTrue(Expected.overlay_user_vehicle == load_vehicle)

    def test_config(self):
        self.config_create_default()
        self.config_create_user()
        self.config_merge()

    def test_config_folder(self):
        shutil.rmtree(self.def_folder)
        shutil.rmtree(self.user_folder)
        self.str_to_file(self.def_folder+'vehicle', FolderConfig.root)
        self.str_to_file(self.def_folder+'/folder/sedan',FolderConfig.car_sedan)
        self.str_to_file(self.def_folder+'/folder/suv', FolderConfig.car_suv)
        cfg = Config(self.def_folder+'vehicle')
        # self.DEBUG = True
        self.dprint('\n'+cfg.dump())
        cfg.overlay(self.user_folder+'vehicle')
        self.dprint('\n'+cfg.dump())
        cfg.store()
        cfg2 = Config(self.user_folder+'vehicle')
        self.dprint('\n'+cfg.dump())
        self.dprint('\n'+cfg2.dump())
        self.assertTrue(cfg.dump() == cfg2.dump())
        for fname in ['vehicle', 'folder/sedan', 'folder/suv']:
            default_load = self.file_to_str(self.def_folder+fname).strip()
            user_load = self.file_to_str(self.user_folder+fname).strip()
            self.assertTrue(default_load == user_load)
