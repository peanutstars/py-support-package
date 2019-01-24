
import os
import shutil
import unittest

from pysp.basic import FileOp
from pysp.error import PyspDebug
from pysp.conf import Config
from pysp.sql import DB



class SqlTest(unittest.TestCase, PyspDebug, FileOp):
    # DEBUG = True
    test_folder     = '/tmp/sql/'
    config_file     = test_folder+'db.cfg'
    db_file         = test_folder+'test.sqlite3'

    def test_db(self):
        if os.path.exists(self.test_folder):
            shutil.rmtree(self.test_folder)
        self.create_db()
        self.alter_db()
        self.upsert_db()
        self.query_db()
        self.count_db()

    def create_db(self):
        DBCONFIG = '''
tables:
    - name: inspection
      columns:
        - [SNumber, String10, NotNull, CollateNocase, Unique, PrimaryKey]
        - [Integer, Integer, NotNull]
        - [Float, Float]
        - [Bool, Boolean]
        - [DateTime, DateTime]
'''
        self.str_to_file(self.config_file, DBCONFIG)
        dbconfig = Config(self.config_file)
        db = DB(self.db_file, dbconfig)
        del db

    def alter_db(self):
        DBCONFIG = '''
tables:
    - name: inspection
      columns:
        - [SNumber, String10, NotNull, CollateNocase, Unique, PrimaryKey]
        - [Integer, Integer, NotNull]
        - [Float, Float]
        - [Bool, Boolean]
        - [DateTime, DateTime]
        - [Alter1, String15, Unique]
        - [Alter2, String5]
'''
        self.str_to_file(self.config_file, DBCONFIG)
        db = DB(self.db_file, Config(self.config_file))
        del db

    def upsert_db(self):
        db = DB(self.db_file, Config(self.config_file))
        items = {
            'SNumber':  '0000000000',
            'Integer':  1234,
        }
        db.upsert('inspection', **items)
        items = {
            'SNumber':  '0000000000',
            'Alter2':   'Five5',
        }
        db.upsert('inspection', **items)
        for i in range(10):
            items = {
                'SNumber':  '%010d' % i,
                'Integer':  9 - i,
                'Alter1':   '%05d' % i,
            }
            db.upsert('inspection', **items)
        del db

    def query_db(self):
        db = DB(self.db_file, Config(self.config_file))
        columns = ['SNumber', 'Integer', 'Float', 'Alter1', 'Alter2']
        options = {
            'wheres': {
                'Alter1': ['00000', '00005'],
                'Alter2': 'Five5',
            },
            'operate': DB.OP_AND,
            'page': 0,
            'size': 4,
        }
        data = db.query('inspection', *columns, **options)
        self.assertTrue(len(data) == 1)
        data = data[0]
        self.assertTrue(data[0] == '0000000000')
        self.assertTrue(data[1] == 9)
        self.assertTrue(data[2] == None)
        self.assertTrue(data[3] == '00000')
        self.assertTrue(data[4] == 'Five5')

        columns = []
        options = {
            'wheres': {
                'Alter1': ['00000', '00005'],
                'Alter2': 'Five5',
            },
            'operate': DB.OP_OR,
            'page': 0,
            'size': 4,
        }
        data = db.query('inspection', *columns, **options)
        self.assertTrue(len(data) == 2)
        for item in data:
            self.assertTrue(item[0] in ['0000000000', '0000000005'])

    def count_db(self):
        db = DB(self.db_file, Config(self.config_file))
        self.assertTrue(db.count('inspection') == 10)
        columns = []
        options = {
            'wheres': {
                'Alter1': ['00000', '005'],
                'Alter2': 'Five5',
            },
            'operate': DB.OP_OR,
            'page': 0,
            'size': 4,
        }
        self.assertTrue(db.count('inspection', *columns, **options) == 2)
        columns = ['SNumber', 'Integer', 'Float', 'Alter1', 'Alter2']
        options = {
            'wheres': {
                'Alter1': ['00000', '00005'],
                'Alter2': 'Five5',
            },
            'operate': DB.OP_AND,
            'page': 0,
            'size': 4,
        }
        self.assertTrue(db.count('inspection', *columns, **options) == 1)
