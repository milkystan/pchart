#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/1/5 14:20
# @Author  : Stan
# @File    : HtGenerator.py

from JsGenerator import JsGen


def yield_counter():
    n = 0
    while True:
        yield n
        n += 1

counter = yield_counter()


class Element(object):
    INDENT_LEN = 4
    ID_PREFIX = 'pDiv_'
    BEGIN = '<{tag} id="{id}" style="width:{width}px;height:{height}px;">\n'
    END = '</{tag}>\n'

    def __init__(self, tag, width, height, id=None, indent=0):
        self.tag = tag
        self.width = width
        self.height = height
        self.indent = indent
        self.children = []
        self.id = id if id else self.ID_PREFIX + str(counter.next())

    def add_child(self, child):
        if isinstance(child, (Element, ScriptElement)):
            self.children.append(child)
            child.adjust_indent(self.indent + self.INDENT_LEN)

    def add_children(self, children):
        for child in children:
            self.add_child(child)

    def remove_children(self):
        self.children = []

    def adjust_indent(self, indent):
        self.indent = indent
        for child in self.children:
            child.adjust_indent(indent + self.INDENT_LEN)

    def build(self):
        html_str = ''
        html_str += ' ' * self.indent + self.BEGIN.format(tag=self.tag, id=self.id, width=self.width, height=self.height)
        for child in self.children:
            html_str += child.build()

        html_str += ' ' * self.indent + self.END.format(tag=self.tag)
        return html_str


class ScriptElement(object):
    TEXT_BEGIN = '<script type="text/javascript">\n'
    LINK_BEGIN = '<script src="{url}">\n'
    END = '</script>\n'
    INDENT_LEN = 4
    TEXT = 0
    LINK = 1

    def __init__(self, tag_type, indent=0, **kwargs):
        self.indent = indent
        self.js = None
        self.tag_type = tag_type
        self.kwargs = kwargs

    def add_script(self, js):
        '''indent won't be adjusted automatically, so this method is not recommended to use'''
        if isinstance(js, JsGen):
            self.js = js

    def create_script(self):
        self.js = JsGen(indent=self.indent + self.INDENT_LEN)
        return self.js

    def adjust_indent(self, indent):
        self.indent = indent

    def build(self):
        html_str = ''
        begin = self.TEXT_BEGIN if self.tag_type is self.TEXT else self.LINK_BEGIN
        html_str += ' ' * self.indent + begin.format(**self.kwargs)
        if self.js:
            html_str += self.js.build()
        html_str += ' ' * self.indent + self.END
        return html_str

if __name__ == '__main__':
    pass