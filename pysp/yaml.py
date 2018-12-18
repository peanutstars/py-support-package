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
    def dump(cls, yo, pretty=True):
        if pretty:
            return yaml.dump(yo, default_flow_style=False, indent=4)
        return yaml.dump(yo)

    # @classmethod
    def merge(self, newy, defy):
        if isinstance(newy, dict) and isinstance(defy, dict):
            for k, v in defy.items():
                if k not in newy:
                    # self.dprint(k, v)
                    newy[k] = v
                else:
                    newy[k] = self.merge(newy[k], v) #if newy[k] else v
        return newy

    # @classmethod
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

    # @classmethod
    def store(self, ymlo, pretty=True):
        def collect(ymlo, xpath=''):
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
            self.dprint('xpath={}, value={}'.format(node.xpath, node.value))
            self.dprint(YAML.dump(ymlo, pretty=pretty))
            del ymlso[YAML.MARK_INCLUDE]
            store_file(ymlso, node)

            ymlso = get_node(ymlo, xpaths[:-1])
            if node.value:
                ymlso[xpaths[-1]] = str(YAML.TAG_INCLUDE + ' ' + node.value)
            self.dprint(YAML.dump(ymlo, pretty=pretty))

        nodes = collect(ymlo)
        # self.DEBUG = True
        for n in nodes:
            self.dprint('{x}|{f}|{v}'.format(x=n.xpath, f=n.fullpath, v=n.value))
            self.dprint('============')
            store_node(ymlo, n)

    # @classmethod
    def store_mark(self, yml, fullpath, node_value):
        if YAML.MARK_INCLUDE in yml:
            emsg = 'Already use %s key in %s' % (YAML.MARK_INCLUDE, fullpath)
            raise PyspError(emsg)
        yml[YAML.MARK_INCLUDE] = {
            'fullpath': fullpath,
            'value': node_value
        }
        return yml

    # @classmethod
    def include(self, loader, node):
        # self.DEBUG = True
        fname = os.path.join(os.path.dirname(loader.name), node.value)
        self.dprint('Include YAML:', fname)
        return self.load(fname, node.value)
