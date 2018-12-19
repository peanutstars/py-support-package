# -*- coding: utf-8 -*-

import codecs
import copy
import collections
import os
import yaml

from pysp.error import PyspDebug, PyspError


YNode = collections.namedtuple('YNode', 'xpath fullpath value')


class YAML(PyspDebug):
    TAG_INCLUDE  = '!include'
    MARK_INCLUDE = '__include__'
    EOL = '\n'

    @classmethod
    def dump(cls, yo, pretty=True):
        if pretty:
            return yaml.dump(yo, default_flow_style=False, indent=4)
        return yaml.dump(yo)

    def merge(self, newy, defy):
        if isinstance(newy, dict) and isinstance(defy, dict):
            for k, v in defy.items():
                if k not in newy:
                    # self.dprint(k, v)
                    newy[k] = v
                else:
                    newy[k] = self.merge(newy[k], v) #if newy[k] else v
        return newy

    def load(self, yml, node_value=None):
        yaml.add_constructor(YAML.TAG_INCLUDE, self.include)
        if os.path.exists(yml):
            with codecs.open(yml, 'r', encoding='utf-8') as fd:
                try:
                    # pass a file descripter, if use '!include' method
                    return self.store_mark(yaml.load(fd), yml, node_value)
                    # return yaml.load(fd)
                except yaml.YAMLError as e:
                    emsg = 'Error YAML Loading: %s\n%s' % (yml, str(e))
                    raise PyspError(emsg)
        try:
            return yaml.load(yml)
        except yaml.YAMLError as e:
            emsg = 'Error YAML Loading: %s\n%s' % (yml, str(e))
            raise PyspError(emsg)

    def collect_node(self, ymlo, xpath=''):
        ns = []
        self.dprint("xpath: '{}'".format(xpath))
        for k, v in ymlo.items():
            xp = xpath
            self.dprint('- ', k)
            if k == self.MARK_INCLUDE:
                self.dprint('+ ', xp)
                n = YNode(xpath=xp,
                          fullpath=ymlo[k]['fullpath'],
                          value=ymlo[k]['value'])
                ns.append(n)
            elif type(ymlo[k]) == dict:
                xp += ('.' if xp else '') + k
                ns += self.collect_node(ymlo[k], xp)
        return ns

    def store(self, ymlo, pretty=True):
        '''Stored yml object to file.  In processing, yml object is changed.'''
        def store_file(ymlo, node):
            dirname = os.path.dirname(os.path.abspath(node.fullpath))
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            self.dprint('W: {}'.format(node.fullpath))
            with codecs.open(node.fullpath, 'w', encoding='utf-8') as fd:
                for line in YAML.dump(ymlo, pretty=pretty).strip().splitlines():
                    if line.find(YAML.TAG_INCLUDE) >= 0:
                        line = line.replace("'", "")
                    fd.write(line + YAML.EOL)

        def get_node(ymlo, xpaths):
            ymlso = ymlo
            if xpaths and xpaths[0]:
                for k in xpaths:
                    ymlso = ymlso[k]
            return ymlso

        def store_node(ymlo, node):
            xpaths = node.xpath.split('.')
            ymlso = get_node(ymlo, xpaths)
            self.dprint('xpath={}, value={}'.format(node.xpath, node.value))
            self.dprint(YAML.dump(ymlo, pretty=pretty))
            del ymlso[YAML.MARK_INCLUDE]
            store_file(ymlso, node)

            ymlso = get_node(ymlo, xpaths[:-1])
            if node.value:
                ymlso[xpaths[-1]] = str(YAML.TAG_INCLUDE + ' ' + node.value)
            self.dprint(YAML.dump(ymlo, pretty=pretty))

        nodes = self.collect_node(ymlo)
        # self.DEBUG = True
        for n in nodes:
            self.dprint('{x}|{f}|{v}'.format(x=n.xpath, f=n.fullpath, v=n.value))
            self.dprint('============')
            store_node(ymlo, n)

    def store_mark(self, yml, fullpath, node_value):
        if YAML.MARK_INCLUDE in yml:
            emsg = 'Already use %s key in %s' % (YAML.MARK_INCLUDE, fullpath)
            raise PyspError(emsg)
        yml[YAML.MARK_INCLUDE] = {
            'fullpath': fullpath,
            'value': node_value
        }
        return yml

    def include(self, loader, node):
        # self.DEBUG = True
        fname = os.path.join(os.path.dirname(loader.name), node.value)
        self.dprint('Include YAML:', fname)
        return self.load(fname, node.value)


class Config(YAML):
    _data = {}

    def __init__(self, yml_file=None):
        self._data = {}
        if yml_file:
            self.loadup(yml_file)

    def dump(self):
        return super(Config, self).dump(self._data)

    def loadup(self, yml_file):
        if not os.path.exists(yml_file):
            raise PyspError('Not Exists: {}'.format(yml_file))
        if self._data:
            self.iprint('Overwrite')
        self._data = self.load(yml_file)

    def _fixup_folder(self, yobject, ymlpath):
        if ymlpath:
            nodes = self.collect_node(yobject)
            dirname = os.path.dirname(ymlpath)
            for n in nodes:
                if n.value:
                    xpath = '{}.{}.fullpath'.format(n.xpath, self.MARK_INCLUDE)
                    fpath = '{}/{}'.format(dirname, n.value)
                    self.set_value(xpath, fpath, yobject=yobject)

    def overlay(self, yml_file):
        if not os.path.exists(yml_file):
            raise PyspError('Not Exists: {}'.format(yml_file))
        newy = super(Config, self).load(yml_file)
        self._data = self.merge(newy, self._data)
        self._fixup_folder(self._data, yml_file)

    def store(self, to_abs=None):
        data = copy.deepcopy(self._data)
        if to_abs:
            fullpath = os.path.abspath(to_abs)
            self.set_value(self.MARK_INCLUDE, {
                'fullpath': fullpath,
                'value': None
            }, yobject=data)
        self._fixup_folder(data, to_abs)
        super(Config, self).store(data)

    def get_value(self, key, defvalue='', yobject=None):
        data = self._data if yobject is None else yobject
        for k in key.split('.'):
            if k in data:
                data = data[k]
            else:
                return defvalue
        return data

    def set_value(self, key, value, yobject=None):
        data = self._data if yobject is None else yobject
        karr = key.split('.')
        depth = len(karr)
        for d in range(depth):
            if karr[d] in data:
                if d == (depth - 1):
                    data[karr[d]] = value
                else:
                    data = data[karr[d]]
            else:
                if d == (depth - 1):
                    data[karr[d]] = value
                else:
                    data[karr[d]] = {}
                    data = data[karr[d]]