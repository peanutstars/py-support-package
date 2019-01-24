#!/usr/bin/env python3

import copy
import sqlalchemy as sa

from sqlalchemy import event, or_, and_
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker


# @event.listens_for(Engine, "connect")
# def set_sqlite_pragma(dbapi_connection, connection_record):
#     module = dbapi_connection.__class__.__module__
#     if module == 'sqlite3':
#         print('------------------------------------------->>>')
#         cursor = dbapi_connection.cursor()
#         cursor.execute("PRAGMA journal_mode=WAL")
#         cursor.execute("PRAGMA foreign_keys=ON")
#         cursor.close()


class SQL(object):

    class Error(Exception):
        pass

    def __init__(self):
        self.meta = sa.MetaData()
        self.engine = None

    def init_tables(self, cfg):
        meta = sa.MetaData(bind=self.engine)
        meta.reflect()
        for dictable in cfg.get_value('tables'):
            self._init_table(meta, dictable)

    def _init_table(self, meta, dictable):
        if dictable['name'] not in meta.tables.keys():
            self._create_table(meta, dictable)
            meta.create_all(self.engine)
        else:
            self._init_columns(meta, dictable)

    def _create_table(self, meta, dictable):
        tablename = dictable['name']
        columns = dictable['columns']
        args = [tablename, meta]
        for colparams in columns:
            args.append(self.build_column(colparams))
        sa.Table(*args)

    def _init_columns(self, meta, dictable):
        tablename = dictable['name']
        columns = dictable['columns']
        for colparam in columns:
            colname = colparam[0]
            if colname in meta.tables[tablename].columns:
                column = meta.tables[tablename].columns[colname]
                coltype = column.type.__class__.__name__
                if not self.is_valid_type(colparam[1], coltype):
                    emsg = 'Column {cn}: Not Matched Type - {a}, {b}'.format(
                        cn=colname, a=colparam[1], b=coltype)
                    raise SQL.Error(emsg)
                if coltype in ['VARCHAR', 'CHAR']:
                    # print('@@@', colname, column.type.collation, column.type.length)
                    length = int(colparam[1][len('String'):])
                    if length != column.type.length:
                        emsg = 'Column {cn}: Not Matched String Length::' \
                            'Expected %d, but %d' % (length, column.type.length)
                        raise SQL.Error(emsg.format(cn=colname))
                if 'PrimaryKey' in colparam and column.primary_key == False:
                    emsg = 'Column {cn}: Not Set Primary Key Property'
                    raise SQL.Error(emsg.format(cn=colname))
                if 'Unique' in colparam and column.unique == False:
                    emsg = 'Column {cn}: Not Set Unique Property'
                    raise SQL.Error(emsg.format(cn=colname))
                if 'NotNull' in colparam and column.nullable == True:
                    emsg = 'Column {cn}: Not Null'
                    raise SQL.Error(emsg.format(cn=colname))
            else:
                colobj = self.build_column(colparam)
                self.add_column(self.engine, tablename, colobj)


    def is_valid_type(cls, config_type, sql_type):
        dbtypes = {
            'INTEGER':  'Integer',
            'FLOAT':    'Float',
            'BOOLEAN':  'Boolean',
            'DATETIME': 'DateTime',
        }
        if sql_type in ['VARCHAR', 'CHAR']:
            return (config_type.find('String') == 0)
        return dbtypes.get(sql_type) == config_type

    def build_column(self, params):
        dbtypes = {
            'Boolean':  sa.Boolean,
            'DateTime': sa.DateTime,
            'Float':    sa.Float,
            'Integer':  sa.Integer,
            'String':   sa.String,
        }
        def build_type(col_type, params):
            if col_type.find('String') == 0:
                args = []
                kwargs = {}
                if len('String') == len(col_type):
                    raise SQL.Error('Need Length of String')
                args.append(int(col_type[len('String'):]))
                if 'CollateNocase' in params:
                    kwargs['collation'] = 'NOCASE'
                return sa.String(*args, **kwargs)
            else:
                try:
                    return dbtypes.get(col_type)()
                except:
                    raise SQL.Error('Unknown Column Type: {}'.format(col_type))

        params = copy.deepcopy(params)
        args = []
        kwargs = {}
        args.append(params.pop(0))
        col_type = params.pop(0)
        args.append(build_type(col_type, params))
        kwargs['nullable'] = False if 'NotNull' in params else True
        kwargs['primary_key'] = True if 'PrimaryKey' in params else False
        kwargs['unique'] = True if 'Unique' in params else False
        # print(str(params), str(args), str(kwargs))
        return sa.Column(*args, **kwargs)

    def add_column(self, engine, table_name, column):
        colname = column.compile(dialect=engine.dialect)
        coltype = column.type.compile(engine.dialect)
        sql = 'ALTER TABLE %s ADD COLUMN %s %s' % (table_name, colname, coltype)
        # print(sql)
        engine.execute(sql)


class DB(SQL):
    OP_AND      = 'and'
    OP_OR       = 'or'
    SQL_PAGE    = 'page'
    SQL_SIZE    = 'size'
    SQL_V_PAGE  = 0
    SQL_V_SIZE  = 5

    def __init__(self, dbpath, config):
        super(DB, self).__init__()
        self.engine = sa.create_engine(
            'sqlite:///{db}'.format(db=dbpath), echo=True)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        if self.session.bind.dialect.name == 'sqlite':
            self.session.execute("PRAGMA journal_mode=WAL")
            self.session.execute("PRAGMA foreign_keys=ON")
            self.session.commit()
        self.init_tables(config)

    def __del__(self):
        self.session.close()

    def to_sql(self, o):
        return str(o.compile(compile_kwargs={"literal_binds": True}))

    def get_table(self, tablename):
        return sa.Table(tablename, self.meta, autoload=True,
                        autoload_with=self.engine)

    def _get_columns(self, table, colnames):
        columns = []
        for col in colnames:
            if col in table.c:
                columns.append(table.c[col])
        return columns if columns else table.c

    def _append_wheres(self, qo, table, **kwargs):
        wheres = kwargs.pop('wheres', {})
        operate = kwargs.pop('operate', self.OP_AND)
        _op = {
            self.OP_AND:    and_,
            self.OP_OR:     or_,
        }
        if wheres:
            filters = []
            for k, v in wheres.items():
                # column = sa.sql.column(k)
                column = table.c[k]
                is_str = column.type.__class__.__name__ in ['VARCHAR', 'CHAR']
                if type(v) is list:
                    _o = None
                    for _v in v:
                        if _o is None:
                            if is_str:
                                _o = or_(column.like('%{}%'.format(_v)))
                            else:
                                _o = or_(column == _v)
                        else:
                            if is_str:
                                _o = or_(column.like('%{}%'.format(_v)), _o)
                            else:
                                _o = or_(column == _v, _o)
                    if _o is not None:
                        filters.append(_o)
                else:
                    if is_str:
                        colike = column.like('%{}%'.format(v))
                        filters.append(_op[operate](colike))
                    else:
                        filters.append(_op[operate](column == v))
            qo = qo.where(_op[operate](*filters))
        return qo

    def _build_query(self, table, *args, **kwargs):
        columns = self._get_columns(table, args)

        qo = sa.sql.select(columns)
        qo = self._append_wheres(qo, table, **kwargs)
        return qo

    def upsert(self, tablename, **kwargs):
        tbl = self.get_table(tablename)
        pk = next(iter(kwargs))
        # pk_column = sa.sql.column(pk)
        pk_column = tbl.c[pk]

        qc = sa.sql.select([tbl.c[pk]]).where(pk_column == kwargs[pk])
        qi = sa.insert(tbl).values(**kwargs)
        qu = sa.update(tbl).values(**kwargs).where(pk_column == kwargs[pk])
        try:
            item = self.session.query(qc).first()
            if item is None:
                self.session.execute(qi)
            else:
                self.session.execute(qu)
            self.session.commit()
        except:
            self.session.rollback()

    def query(self, tablename, *args, **kwargs):
        size = kwargs.pop(self.SQL_SIZE, self.SQL_V_SIZE)
        page = kwargs.pop(self.SQL_PAGE, self.SQL_V_PAGE)

        tbl = self.get_table(tablename)
        qo = self._build_query(tbl, *args, **kwargs)
        qo = qo.limit(size)
        qo = qo.offset(page*size)

        try:
            return self.session.query(qo).all()
        except:
            raise DB.Error('Query: {}'.format(self.to_sql(qo)))

    def count(self, tablename, *args, **kwargs):
        tbl = self.get_table(tablename)
        qo = self._build_query(tbl, *args, **kwargs)
        try:
            return self.session.query(qo).count()
        except:
            raise DB.Error('Count: {}'.format(self.to_sql(qo)))
