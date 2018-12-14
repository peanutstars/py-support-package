# -*- coding: utf-8 -*-

import codecs
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
    def load(cls, yml, node_value=None):
        yaml.add_constructor(YAML.TAG_INCLUDE, cls.include)
        if os.path.exists(yml):
            with codecs.open(yml, 'r', encoding='utf-8') as fd:
                try:
                    # pass a file descripter, if use '!include' method
                    return cls.store_mark(yaml.load(fd), yml, node_value)
                    # return yaml.load(fd)
                except yaml.YAMLError as e:
                    emsg = 'Error YAML Loading: %s\n%s' % (yml, str(e))
                    raise PyspError(emsg)
        try:
            return yaml.load(yml)
        except yaml.YAMLError as e:
            emsg = 'Error YAML Loading: %s\n%s' % (yml, str(e))
            raise PyspError(emsg)

    @classmethod
    def store(cls, ymlo, pretty=True):
        def collect(ymlo, xpath=''):
            ns = []
            cls.dprint("xpath: '{}'".format(xpath))
            for k, v in ymlo.items():
                xp = xpath
                cls.dprint('- ', k)
                if k == cls.MARK_INCLUDE:
                    cls.dprint('+ ', xp)
                    n = YNode(xpath=xp,
                              fullpath=ymlo[k]['fullpath'],
                              value=ymlo[k]['value'])
                    ns.append(n)
                elif type(ymlo[k]) == dict:
                    xp += ('.' if xp else '') + k
                    ns += collect(ymlo[k], xp)
            return ns

        def store_file(ymlo, node):
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
            cls.dprint('xpath={}, value={}'.format(node.xpath, node.value))
            cls.dprint(YAML.dump(ymlo, pretty=pretty))
            del ymlso[YAML.MARK_INCLUDE]
            store_file(ymlso, node)

            ymlso = get_node(ymlo, xpaths[:-1])
            if node.value:
                ymlso[xpaths[-1]] = str(YAML.TAG_INCLUDE + ' ' + node.value)
            cls.dprint(YAML.dump(ymlo, pretty=pretty))

        nodes = collect(ymlo)
        # cls.DEBUG = True
        for n in nodes:
            cls.dprint('{x}|{f}|{v}'.format(x=n.xpath, f=n.fullpath, v=n.value))
            cls.dprint('============')
            store_node(ymlo, n)

    @classmethod
    def store_mark(cls, yml, fullpath, node_value):
        if YAML.MARK_INCLUDE in yml:
            emsg = 'Already use %s key in %s' % (YAML.MARK_INCLUDE, fullpath)
            raise PyspError(emsg)
        yml[YAML.MARK_INCLUDE] = {
            'fullpath': fullpath,
            'value': node_value
        }
        return yml

    @classmethod
    def include(cls, loader, node):
        # cls.DEBUG = True
        fname = os.path.join(os.path.dirname(loader.name), node.value)
        cls.dprint('Include YAML:', fname)
        return cls.load(fname, node.value)

    @classmethod
    def merge(cls, ya, yb):
        if isinstance(ya, dict) and isinstance(yb, dict):
            for k, v in yb.items():
                if k not in ya:
                    ya[k] = v
                else:
                    ya[k] = cls.merge(ya[k], v)
            return ya
        raise PyspError('Error Type: ya or yb')

    @classmethod
    def dump(cls, yo, pretty=True):
        if pretty:
            return yaml.dump(yo, default_flow_style=False, indent=4)
        return yaml.dump(yo)
